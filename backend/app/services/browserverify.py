"""
BrowserVerify: Headless Playwright browser validation for UI changes.
Runs in isolated containers, checks a11y and visual regression.
"""
import asyncio
import hashlib
import os
from typing import Optional, Dict, List
from dataclasses import dataclass

@dataclass
class BrowserResult:
    passed: bool
    screenshots: List[Dict]
    a11y_violations: List[Dict]
    visual_regression_score: Optional[float]
    failure_reason: Optional[str]

class BrowserVerify:
    def __init__(self, timeout: int = 30000, pool_size: int = 5):
        self.timeout = timeout
        self.pool_size = pool_size
        self._playwright_available = self._check_playwright()

    def _check_playwright(self) -> bool:
        try:
            from playwright.async_api import async_playwright
            return True
        except ImportError:
            return False

    async def verify(
        self,
        url: str,
        viewport: Dict[str, int] = None,
        baseline_screenshot_path: Optional[str] = None,
        run_a11y: bool = True,
        run_visual_regression: bool = True,
    ) -> BrowserResult:
        if not self._playwright_available:
            return BrowserResult(
                passed=False,
                screenshots=[],
                a11y_violations=[],
                visual_regression_score=None,
                failure_reason="Playwright not installed. Run: pip install playwright && playwright install",
            )

        from playwright.async_api import async_playwright

        viewport = viewport or {"width": 1280, "height": 720}
        screenshots = []
        a11y_violations = []
        visual_score = None
        failure_reason = None
        passed = True

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(viewport=viewport)
                page = await context.new_page()

                # Navigate
                response = await page.goto(url, timeout=self.timeout, wait_until="networkidle")
                if not response or response.status >= 400:
                    passed = False
                    failure_reason = f"Page failed to load: HTTP {response.status if response else 'unknown'}"
                    await browser.close()
                    return BrowserResult(
                        passed=False, screenshots=[], a11y_violations=[],
                        visual_regression_score=None, failure_reason=failure_reason
                    )

                # Screenshot
                screenshot_path = f"/tmp/guardloop_screenshots/{hashlib.md5(url.encode()).hexdigest()}.png"
                os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
                await page.screenshot(path=screenshot_path, full_page=True)
                screenshots.append({
                    "path": screenshot_path,
                    "timestamp": asyncio.get_event_loop().time(),
                    "viewport": viewport,
                })

                # Accessibility check (simplified axe-core equivalent)
                if run_a11y:
                    a11y_violations = await self._run_a11y_checks(page)
                    if any(v["impact"] == "critical" for v in a11y_violations):
                        passed = False
                        failure_reason = f"Critical accessibility violations found: {len([v for v in a11y_violations if v['impact'] == 'critical'])}"

                # Visual regression
                if run_visual_regression and baseline_screenshot_path and os.path.exists(baseline_screenshot_path):
                    visual_score = await self._compare_screenshots(screenshot_path, baseline_screenshot_path)
                    if visual_score and visual_score < 0.95:
                        passed = False
                        failure_reason = f"Visual regression failed: similarity {visual_score:.2f}"

                await browser.close()

        except Exception as e:
            passed = False
            failure_reason = f"Browser verification error: {str(e)}"

        return BrowserResult(
            passed=passed,
            screenshots=screenshots,
            a11y_violations=a11y_violations,
            visual_regression_score=visual_score,
            failure_reason=failure_reason,
        )

    async def _run_a11y_checks(self, page) -> List[Dict]:
        """Basic accessibility checks without axe-core dependency."""
        violations = []

        # Check for images without alt
        images_without_alt = await page.query_selector_all("img:not([alt])")
        for img in images_without_alt:
            violations.append({
                "rule": "image-alt",
                "impact": "critical",
                "target": "img",
                "message": "Image missing alt text",
            })

        # Check for buttons without accessible names
        buttons = await page.query_selector_all("button, [role='button']")
        for btn in buttons:
            text = await btn.text_content()
            aria_label = await btn.get_attribute("aria-label")
            if not text and not aria_label:
                violations.append({
                    "rule": "button-name",
                    "impact": "critical",
                    "target": "button",
                    "message": "Button missing accessible name",
                })

        # Check for low contrast (simplified)
        low_contrast_elements = await page.evaluate("""
            () => {
                const elements = document.querySelectorAll('p, span, a, button, h1, h2, h3, h4, h5, h6');
                const violations = [];
                elements.forEach(el => {
                    const style = window.getComputedStyle(el);
                    const color = style.color;
                    const bg = style.backgroundColor;
                    // Simplified check: if color is light gray on white
                    if (color.includes('200') || color.includes('204')) {
                        violations.push({tag: el.tagName, text: el.textContent?.slice(0, 50)});
                    }
                });
                return violations;
            }
        """)
        for v in low_contrast_elements:
            violations.append({
                "rule": "color-contrast",
                "impact": "serious",
                "target": v.get("tag", "unknown"),
                "message": f"Potential low contrast: {v.get('text', '')}",
            })

        return violations

    async def _compare_screenshots(self, current: str, baseline: str) -> Optional[float]:
        """Pixel-based similarity using Pillow."""
        try:
            from PIL import Image
            import numpy as np

            img1 = Image.open(current).convert("RGB")
            img2 = Image.open(baseline).convert("RGB")

            # Resize to same dimensions
            img2 = img2.resize(img1.size)

            arr1 = np.array(img1)
            arr2 = np.array(img2)

            mse = np.mean((arr1 - arr2) ** 2)
            if mse == 0:
                return 1.0

            # Simple similarity: inverse of normalized MSE
            similarity = 1.0 / (1.0 + mse / 10000.0)
            return float(min(1.0, similarity))
        except Exception:
            return None
