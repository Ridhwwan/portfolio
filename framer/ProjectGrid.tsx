/**
 * Framer Code Component — Python Portfolio Grid
 *
 * Fetches project data from a JSON endpoint (Notion → integration → JSON)
 * and renders an auto-sorted grid of interactive project cards.
 *
 * SETUP OPTIONS (pick one):
 *
 * Option A — Direct Notion API (requires a proxy/serverless function since
 *            Notion API needs auth headers that can't be sent from browser):
 *            Deploy a small API route that queries Notion and returns JSON.
 *
 * Option B — Use a service like Notion2JSON, Super, or a Cloudflare Worker
 *            to expose your Notion database as a public JSON endpoint.
 *
 * Option C — Read from the raw manifest.json in your GitHub repo
 *            (simpler, but loses the Notion sorting/pinning features).
 *
 * Replace PROJECTS_API_URL below with your endpoint.
 */

import { useEffect, useState } from "react"

// ─── CONFIGURATION ──────────────────────────────────────────
const PROJECTS_API_URL = "https://YOUR_ENDPOINT/api/projects"
// Replace with your actual endpoint that returns the project JSON array
// ─────────────────────────────────────────────────────────────

interface Project {
    name: string
    description: string
    url: string
    platform: "streamlit" | "gradio" | "pyscript"
    tags: string[]
    lastUpdated: string
    sortOrder: number | null
    thumbnail?: string
}

const PLATFORM_COLORS: Record<string, string> = {
    streamlit: "#FF4B4B",
    gradio: "#F89820",
    pyscript: "#4B8BBE",
}

const PLATFORM_LABELS: Record<string, string> = {
    streamlit: "Streamlit",
    gradio: "Gradio",
    pyscript: "In-Browser",
}

function sortProjects(projects: Project[]): Project[] {
    return [...projects].sort((a, b) => {
        // pinned items (with sortOrder set) come first, in their order
        if (a.sortOrder != null && b.sortOrder != null)
            return a.sortOrder - b.sortOrder
        if (a.sortOrder != null) return -1
        if (b.sortOrder != null) return 1
        // everything else: most recently updated first
        return (
            new Date(b.lastUpdated).getTime() -
            new Date(a.lastUpdated).getTime()
        )
    })
}

export default function ProjectGrid() {
    const [projects, setProjects] = useState<Project[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState("")
    const [activeEmbed, setActiveEmbed] = useState<string | null>(null)

    useEffect(() => {
        fetch(PROJECTS_API_URL)
            .then((res) => {
                if (!res.ok) throw new Error(`HTTP ${res.status}`)
                return res.json()
            })
            .then((data) => {
                setProjects(sortProjects(data))
                setLoading(false)
            })
            .catch((err) => {
                setError(err.message)
                setLoading(false)
            })
    }, [])

    if (loading) {
        return (
            <div style={{ padding: 40, textAlign: "center", color: "#666" }}>
                Loading projects...
            </div>
        )
    }

    if (error) {
        return (
            <div style={{ padding: 40, textAlign: "center", color: "#ff4444" }}>
                Failed to load projects: {error}
            </div>
        )
    }

    return (
        <div
            style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fill, minmax(320px, 1fr))",
                gap: 20,
                padding: 20,
                width: "100%",
            }}
        >
            {projects.map((p, i) => (
                <div
                    key={i}
                    style={{
                        background: "#111",
                        border: "1px solid #222",
                        borderRadius: 12,
                        overflow: "hidden",
                        transition: "border-color 0.2s",
                    }}
                    onMouseEnter={(e) =>
                        (e.currentTarget.style.borderColor = "#444")
                    }
                    onMouseLeave={(e) =>
                        (e.currentTarget.style.borderColor = "#222")
                    }
                >
                    {/* card header */}
                    <div style={{ padding: 20, paddingBottom: 12 }}>
                        <div
                            style={{
                                display: "flex",
                                justifyContent: "space-between",
                                alignItems: "flex-start",
                                marginBottom: 8,
                            }}
                        >
                            <h3
                                style={{
                                    margin: 0,
                                    fontSize: 16,
                                    fontWeight: 600,
                                    color: "#eee",
                                }}
                            >
                                {p.name}
                            </h3>
                            <span
                                style={{
                                    background:
                                        PLATFORM_COLORS[p.platform] || "#555",
                                    color: "white",
                                    padding: "2px 8px",
                                    borderRadius: 4,
                                    fontSize: 11,
                                    fontWeight: 500,
                                    whiteSpace: "nowrap",
                                }}
                            >
                                {PLATFORM_LABELS[p.platform] || p.platform}
                            </span>
                        </div>

                        <p
                            style={{
                                margin: 0,
                                fontSize: 13,
                                color: "#888",
                                lineHeight: 1.4,
                            }}
                        >
                            {p.description}
                        </p>

                        {/* tags */}
                        <div
                            style={{
                                display: "flex",
                                flexWrap: "wrap",
                                gap: 6,
                                marginTop: 12,
                            }}
                        >
                            {p.tags.map((t) => (
                                <span
                                    key={t}
                                    style={{
                                        background: "#1a1a1a",
                                        border: "1px solid #2a2a2a",
                                        padding: "3px 8px",
                                        borderRadius: 6,
                                        fontSize: 11,
                                        color: "#999",
                                    }}
                                >
                                    {t}
                                </span>
                            ))}
                        </div>
                    </div>

                    {/* action buttons */}
                    <div
                        style={{
                            display: "flex",
                            borderTop: "1px solid #1a1a1a",
                        }}
                    >
                        <button
                            onClick={() =>
                                setActiveEmbed(
                                    activeEmbed === p.url ? null : p.url
                                )
                            }
                            style={{
                                flex: 1,
                                padding: "10px 0",
                                background: "none",
                                border: "none",
                                borderRight: "1px solid #1a1a1a",
                                color: "#aaa",
                                fontSize: 12,
                                cursor: "pointer",
                            }}
                        >
                            {activeEmbed === p.url ? "Close" : "Try It"}
                        </button>
                        <button
                            onClick={() => window.open(p.url, "_blank")}
                            style={{
                                flex: 1,
                                padding: "10px 0",
                                background: "none",
                                border: "none",
                                color: "#aaa",
                                fontSize: 12,
                                cursor: "pointer",
                            }}
                        >
                            Open ↗
                        </button>
                    </div>

                    {/* embedded iframe — toggles on "Try It" */}
                    {activeEmbed === p.url && (
                        <div
                            style={{
                                borderTop: "1px solid #1a1a1a",
                                background: "#0a0a0a",
                            }}
                        >
                            <iframe
                                src={p.url}
                                width="100%"
                                height="450"
                                style={{
                                    border: "none",
                                    display: "block",
                                }}
                                title={p.name}
                            />
                        </div>
                    )}
                </div>
            ))}
        </div>
    )
}
