"use client";

import { useEffect, useRef, useState } from "react";
import { ZoomIn, ZoomOut, Maximize2, Filter } from "lucide-react";

interface Node {
  id: string;
  name: string;
  x: number;
  y: number;
  status: string;
}

const STATUS_COLORS: Record<string, { fill: string; stroke: string; text: string }> = {
  completed: { fill: "#10B981", stroke: "#059669", text: "#FFFFFF" },
  running: { fill: "#3B82F6", stroke: "#1D4ED8", text: "#FFFFFF" },
  blocked: { fill: "#EF4444", stroke: "#B91C1C", text: "#FFFFFF" },
  failed: { fill: "#F43F5E", stroke: "#BE123C", text: "#FFFFFF" },
  pending: { fill: "#6B7280", stroke: "#374151", text: "#FFFFFF" },
};

export function TaskGraphViz({
  nodes,
  edges,
  criticalPath,
}: {
  nodes: any[];
  edges: any[];
  criticalPath: string[];
}) {
  const svgRef = useRef<SVGSVGElement>(null);
  const [scale, setScale] = useState(1.0);
  const [onlyConnected, setOnlyConnected] = useState(true);

  // Filter nodes if onlyConnected is active
  const filteredNodes = onlyConnected && edges.length > 0
    ? nodes.filter((n) => edges.some((e) => e.from === n.id || e.to === n.id))
    : nodes;

  useEffect(() => {
    const svg = svgRef.current;
    if (!svg) return;
    svg.innerHTML = "";

    if (!filteredNodes || filteredNodes.length === 0) return;

    // Defs for markers
    const defs = document.createElementNS("http://www.w3.org/2000/svg", "defs");
    defs.innerHTML = `
      <marker id="arrow-default" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">
        <path d="M 0 0 L 10 5 L 0 10 z" fill="#3B82F6" />
      </marker>
      <marker id="arrow-critical" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="9" markerHeight="9" orient="auto-start-reverse">
        <path d="M 0 0 L 10 5 L 0 10 z" fill="#EF4444" />
      </marker>
    `;
    svg.appendChild(defs);

    const nodeMap = new Map<string, Node>();
    const total = filteredNodes.length;
    const cols = Math.min(5, Math.max(3, Math.ceil(Math.sqrt(total))));

    filteredNodes.forEach((n, i) => {
      const col = i % cols;
      const row = Math.floor(i / cols);
      nodeMap.set(n.id, {
        id: n.id,
        name: n.name || n.id.slice(0, 8),
        x: 100 + col * 160,
        y: 70 + row * 100,
        status: n.status || "pending",
      });
    });

    // Draw Edges
    edges.forEach((e) => {
      const from = nodeMap.get(e.from);
      const to = nodeMap.get(e.to);
      if (!from || !to) return;

      const isCritical = criticalPath.includes(e.from) && criticalPath.includes(e.to);
      const dx = to.x - from.x;
      const dy = to.y - from.y;
      const dist = Math.sqrt(dx * dx + dy * dy) || 1;
      const uX = dx / dist;
      const uY = dy / dist;

      const radius = 22;
      const startX = from.x + uX * radius;
      const startY = from.y + uY * radius;
      const endX = to.x - uX * (radius + 8);
      const endY = to.y - uY * (radius + 8);

      const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
      line.setAttribute("x1", String(startX));
      line.setAttribute("y1", String(startY));
      line.setAttribute("x2", String(endX));
      line.setAttribute("y2", String(endY));
      line.setAttribute("stroke", isCritical ? "#EF4444" : "#3B82F6");
      line.setAttribute("stroke-width", isCritical ? "3" : "2");
      if (isCritical) line.setAttribute("stroke-dasharray", "5,3");
      line.setAttribute("marker-end", isCritical ? "url(#arrow-critical)" : "url(#arrow-default)");
      svg.appendChild(line);
    });

    // Draw Nodes
    nodeMap.forEach((node) => {
      const g = document.createElementNS("http://www.w3.org/2000/svg", "g");
      const isCritical = criticalPath.includes(node.id);
      const colors = STATUS_COLORS[node.status] || STATUS_COLORS["pending"];

      const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
      circle.setAttribute("cx", String(node.x));
      circle.setAttribute("cy", String(node.y));
      circle.setAttribute("r", "22");
      circle.setAttribute("fill", colors.fill);
      circle.setAttribute("stroke", isCritical ? "#EF4444" : colors.stroke);
      circle.setAttribute("stroke-width", isCritical ? "3" : "2");
      circle.setAttribute("class", "transition-all duration-300 hover:scale-110 cursor-pointer");
      g.appendChild(circle);

      // Node ID Label inside circle
      const idText = document.createElementNS("http://www.w3.org/2000/svg", "text");
      idText.setAttribute("x", String(node.x));
      idText.setAttribute("y", String(node.y + 4));
      idText.setAttribute("text-anchor", "middle");
      idText.setAttribute("font-size", "10");
      idText.setAttribute("font-weight", "700");
      idText.setAttribute("fill", colors.text);
      idText.textContent = node.id.slice(0, 5);
      g.appendChild(idText);

      // Task Name Label under circle
      const nameText = document.createElementNS("http://www.w3.org/2000/svg", "text");
      nameText.setAttribute("x", String(node.x));
      nameText.setAttribute("y", String(node.y + 36));
      nameText.setAttribute("text-anchor", "middle");
      nameText.setAttribute("font-size", "10");
      nameText.setAttribute("fill", "#94A3B8");
      nameText.setAttribute("class", "font-sans");
      const shortName = node.name.length > 20 ? node.name.slice(0, 18) + "…" : node.name;
      nameText.textContent = shortName;
      g.appendChild(nameText);

      // Tooltip
      const title = document.createElementNS("http://www.w3.org/2000/svg", "title");
      title.textContent = `${node.name} (${node.status.toUpperCase()})\nID: ${node.id}`;
      g.appendChild(title);

      svg.appendChild(g);
    });
  }, [filteredNodes, edges, criticalPath]);

  const cols = Math.min(5, Math.max(3, Math.ceil(Math.sqrt(filteredNodes.length || 1))));
  const rows = Math.ceil((filteredNodes.length || 1) / cols);
  const viewBoxWidth = Math.max(650, cols * 170 + 40);
  const viewBoxHeight = Math.max(320, rows * 110 + 60);

  return (
    <div className="space-y-3">
      {/* Controls Bar */}
      <div className="flex items-center justify-between bg-muted/5 px-3 py-2 border border-border rounded-md text-xs">
        <div className="flex items-center gap-2">
          <button
            onClick={() => setOnlyConnected(!onlyConnected)}
            className={`flex items-center gap-1.5 px-2.5 py-1 rounded-md font-medium transition-colors ${
              onlyConnected
                ? "bg-primary/10 text-primary border border-primary/20"
                : "bg-muted text-muted-foreground hover:bg-muted/80"
            }`}
          >
            <Filter className="w-3.5 h-3.5" />
            {onlyConnected ? "Showing Connected Tasks" : "Showing All Tasks"}
          </button>
          <span className="text-muted-foreground">
            ({filteredNodes.length} nodes, {edges.length} dependencies)
          </span>
        </div>
        <div className="flex items-center gap-1">
          <button
            onClick={() => setScale((s) => Math.max(0.6, s - 0.15))}
            className="p-1 hover:bg-muted rounded text-muted-foreground"
            title="Zoom Out"
          >
            <ZoomOut className="w-4 h-4" />
          </button>
          <span className="w-12 text-center font-mono text-[11px] text-muted">
            {Math.round(scale * 100)}%
          </span>
          <button
            onClick={() => setScale((s) => Math.min(2.0, s + 0.15))}
            className="p-1 hover:bg-muted rounded text-muted-foreground"
            title="Zoom In"
          >
            <ZoomIn className="w-4 h-4" />
          </button>
          <button
            onClick={() => setScale(1.0)}
            className="p-1 hover:bg-muted rounded text-muted-foreground ml-1"
            title="Reset Zoom"
          >
            <Maximize2 className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* SVG Canvas Container */}
      <div className="border border-border rounded-md bg-card overflow-auto max-h-[420px]">
        <div
          style={{ transform: `scale(${scale})`, transformOrigin: "top left" }}
          className="transition-transform duration-200"
        >
          <svg
            ref={svgRef}
            viewBox={`0 0 ${viewBoxWidth} ${viewBoxHeight}`}
            style={{ width: `${viewBoxWidth}px`, height: `${viewBoxHeight}px` }}
            className="block"
          />
        </div>
      </div>
    </div>
  );
}
