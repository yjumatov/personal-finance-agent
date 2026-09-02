"""
Generates a standalone, self-contained HTML report from eval results.
No external dependencies — uses only the Python standard library.
"""

import html
import json
from datetime import datetime


# ── helpers ──────────────────────────────────────────────────────────────────

def _esc(text: str) -> str:
    return html.escape(str(text))


def _score_color(score: int, max_score: int = 12) -> str:
    ratio = score / max_score
    if ratio >= 0.78:
        return "#2e7d32"   # green
    if ratio >= 0.44:
        return "#f57c00"   # amber
    return "#c62828"       # red


def _bar(score: int, max_score: int = 3) -> str:
    pct = int(score / max_score * 100)
    color = _score_color(score, max_score)
    return (
        f'<div style="background:#e0e0e0;border-radius:4px;height:12px;width:100%;">'
        f'<div style="background:{color};width:{pct}%;height:12px;border-radius:4px;"></div>'
        f'</div>'
    )


def _usage_table(usage: dict) -> str:
    if not usage:
        return "<p><em>No usage data</em></p>"
    rows = ""
    for agent in ("analyzer", "recommender", "budget_planner"):
        u = usage.get(agent, {})
        rows += (
            f"<tr><td>{agent.replace('_', ' ').title()}</td>"
            f"<td>{u.get('input_tokens', 0):,}</td>"
            f"<td>{u.get('output_tokens', 0):,}</td>"
            f"<td>{u.get('input_tokens', 0) + u.get('output_tokens', 0):,}</td></tr>"
        )
    rows += (
        f"<tr style='font-weight:bold;border-top:2px solid #aaa;'>"
        f"<td>Total</td>"
        f"<td>{usage.get('total_input_tokens', 0):,}</td>"
        f"<td>{usage.get('total_output_tokens', 0):,}</td>"
        f"<td>{usage.get('total_input_tokens', 0) + usage.get('total_output_tokens', 0):,}</td></tr>"
    )
    return (
        "<table class='usage-table'>"
        "<thead><tr><th>Agent</th><th>Input tokens</th><th>Output tokens</th><th>Total</th></tr></thead>"
        f"<tbody>{rows}</tbody></table>"
    )


# ── per-scenario card ─────────────────────────────────────────────────────────

def _scenario_card(r: dict, idx: int) -> str:
    name = _esc(r["name"])
    desc = _esc(r["description"])

    if r["status"] == "error":
        return (
            f'<div class="card error">'
            f'<h2>{idx+1}. {name}</h2>'
            f'<p><em>{desc}</em></p>'
            f'<p class="error-msg">⚠ Pipeline error: {_esc(r.get("error", "unknown"))}</p>'
            f'</div>'
        )

    scores = r["scores"]
    usage  = r.get("usage") or {}
    outputs = r.get("outputs") or {}
    grounding = scores.get("grounding_evidence") or {}

    score_color = _score_color(scores["total"], scores["max"])

    expenses_html = "<table class='usage-table'><thead><tr><th>Date</th><th>Description</th><th>Amount</th><th>Category</th></tr></thead><tbody>"
    for e in (r.get("expenses") or []):
        expenses_html += (
            f"<tr><td>{_esc(e.get('date',''))}</td>"
            f"<td>{_esc(e.get('description',''))}</td>"
            f"<td>${e.get('amount',0):.2f}</td>"
            f"<td>{_esc(e.get('category',''))}</td></tr>"
        )
    expenses_html += "</tbody></table>"

    def output_section(label: str, key: str) -> str:
        text = outputs.get(key, "")
        return (
            f'<details><summary><strong>{label}</strong></summary>'
            f'<pre class="output-pre">{_esc(text)}</pre>'
            f'</details>'
        )

    grounding_warn = " warn-box" if grounding.get("score", 0) == 0 else ""
    hallucinated = grounding.get("hallucinated_amounts") or []
    hallucinated_str = ", ".join(f"${a:,.2f}" for a in hallucinated) if hallucinated else "none"

    grounding_html = f"""
  <h3>Grounding Evidence</h3>
  <table class="usage-table{grounding_warn}">
    <tbody>
      <tr><td>Expected total (computed from input)</td><td>${grounding.get("expected_total", 0):,.2f}</td></tr>
      <tr><td>Total appears in analysis</td><td>{"yes" if grounding.get("total_found") else "no"}</td></tr>
      <tr><td>Category subtotals matched</td><td>{grounding.get("categories_matched", 0)} / {grounding.get("categories_total", 0)}</td></tr>
      <tr><td>Hallucinated amounts</td><td>{_esc(hallucinated_str)}</td></tr>
    </tbody>
  </table>
"""
    if grounding.get("no_amounts_found"):
        grounding_html += '  <p class="error-msg">⚠ No dollar amounts found in the analysis at all.</p>\n'

    return f"""
<div class="card">
  <h2>{idx+1}. {name}</h2>
  <p class="desc">{desc}</p>

  <div class="score-badge" style="color:{score_color};">
    Score: {scores["total"]}/{scores["max"]}
  </div>

  <div class="score-grid">
    <div>
      <span class="label">Analysis ({scores["analysis"]}/3)</span>
      {_bar(scores["analysis"])}
    </div>
    <div>
      <span class="label">Recommendations ({scores["recommendations"]}/3)</span>
      {_bar(scores["recommendations"])}
    </div>
    <div>
      <span class="label">Budget Plan ({scores["budget"]}/3)</span>
      {_bar(scores["budget"])}
    </div>
    <div>
      <span class="label">Grounding ({scores["grounding"]}/3)</span>
      {_bar(scores["grounding"])}
    </div>
  </div>
  {grounding_html}
  <h3>Token Usage</h3>
  {_usage_table(usage)}

  <h3>Input Expenses</h3>
  {expenses_html}

  <h3>Agent Outputs</h3>
  {output_section("Expense Analysis", "analysis")}
  {output_section("Recommendations", "recommendations")}
  {output_section("Budget Plan", "budget")}
</div>
"""


# ── summary table ─────────────────────────────────────────────────────────────

def _summary_table(results: list[dict]) -> str:
    rows = ""
    for r in results:
        name = _esc(r["name"])
        if r["status"] == "error":
            rows += f"<tr><td>{name}</td><td colspan='6' class='error-msg'>Error</td></tr>"
            continue
        s = r["scores"]
        u = r.get("usage") or {}
        color = _score_color(s["total"], s["max"])
        grounding_cell = f"{s['grounding']}/3"
        if s["grounding"] == 0:
            grounding_cell = "<strong style='color:#c62828;'>0/3 ⚠</strong>"
        rows += (
            f"<tr>"
            f"<td>{name}</td>"
            f"<td style='color:{color};font-weight:bold;'>{s['total']}/{s['max']}</td>"
            f"<td>{s['analysis']}/3</td>"
            f"<td>{s['recommendations']}/3</td>"
            f"<td>{s['budget']}/3</td>"
            f"<td>{grounding_cell}</td>"
            f"<td>{u.get('total_input_tokens',0):,} / {u.get('total_output_tokens',0):,}</td>"
            f"</tr>"
        )
    return (
        "<table class='usage-table'>"
        "<thead><tr>"
        "<th>Scenario</th><th>Total score</th><th>Analysis</th>"
        "<th>Recommendations</th><th>Budget</th><th>Grounding</th><th>Tokens in/out</th>"
        "</tr></thead>"
        f"<tbody>{rows}</tbody></table>"
    )


# ── aggregate stats ───────────────────────────────────────────────────────────

def _aggregate(results: list[dict]) -> str:
    ok = [r for r in results if r["status"] == "success"]
    if not ok:
        return "<p>No successful runs to aggregate.</p>"

    avg_score   = sum(r["scores"]["total"] for r in ok) / len(ok)
    avg_max     = sum(r["scores"]["max"] for r in ok) / len(ok)
    avg_in      = sum((r.get("usage") or {}).get("total_input_tokens",  0) for r in ok) / len(ok)
    avg_out     = sum((r.get("usage") or {}).get("total_output_tokens", 0) for r in ok) / len(ok)
    total_in    = sum((r.get("usage") or {}).get("total_input_tokens",  0) for r in ok)
    total_out   = sum((r.get("usage") or {}).get("total_output_tokens", 0) for r in ok)
    zero_grounding = sum(1 for r in ok if r["scores"]["grounding"] == 0)

    return f"""
<div class="aggregate">
  <div class="stat"><span class="stat-num">{avg_score:.1f}/{avg_max:.0f}</span><br>avg score</div>
  <div class="stat"><span class="stat-num">{avg_in:,.0f}</span><br>avg input tokens/run</div>
  <div class="stat"><span class="stat-num">{avg_out:,.0f}</span><br>avg output tokens/run</div>
  <div class="stat"><span class="stat-num">{total_in + total_out:,}</span><br>total tokens ({len(ok)} runs)</div>
  <div class="stat"><span class="stat-num" style="color:{'#c62828' if zero_grounding else '#2e7d32'};">{zero_grounding}/{len(ok)}</span><br>scenarios with zero grounding</div>
</div>
"""


# ── full HTML document ────────────────────────────────────────────────────────

CSS = """
* { box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
       background: #f5f5f5; color: #212121; margin: 0; padding: 24px; }
h1 { font-size: 1.8rem; margin-bottom: 4px; }
.subtitle { color: #616161; margin-bottom: 32px; font-size: .95rem; }
.card { background: #fff; border-radius: 10px; padding: 24px;
        margin-bottom: 24px; box-shadow: 0 1px 4px rgba(0,0,0,.12); }
.card.error { border-left: 4px solid #c62828; }
.error-msg { color: #c62828; }
h2 { font-size: 1.25rem; margin: 0 0 4px; }
h3 { font-size: 1rem; margin: 20px 0 8px; color: #424242; }
.desc { color: #757575; margin: 0 0 16px; font-size: .9rem; }
.score-badge { font-size: 1.5rem; font-weight: 700; margin: 8px 0 16px; }
.score-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px;
              margin-bottom: 20px; }
.label { font-size: .8rem; color: #616161; display: block; margin-bottom: 4px; }
.usage-table { width: 100%; border-collapse: collapse; font-size: .88rem; }
.usage-table th { text-align: left; background: #eeeeee; padding: 6px 10px;
                  border-bottom: 2px solid #bdbdbd; }
.usage-table td { padding: 5px 10px; border-bottom: 1px solid #e0e0e0; }
.usage-table.warn-box { outline: 2px solid #c62828; border-radius: 4px; }
details { margin-bottom: 8px; }
summary { cursor: pointer; padding: 6px; background: #f5f5f5;
          border-radius: 4px; font-size: .9rem; }
.output-pre { white-space: pre-wrap; word-break: break-word;
              background: #fafafa; border: 1px solid #e0e0e0;
              border-radius: 4px; padding: 12px; font-size: .82rem;
              max-height: 320px; overflow-y: auto; }
.aggregate { display: flex; gap: 16px; flex-wrap: wrap; margin: 16px 0; }
.stat { background: #fff; border-radius: 8px; padding: 16px 24px;
        text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,.1);
        flex: 1; min-width: 140px; }
.stat-num { font-size: 1.5rem; font-weight: 700; color: #1565c0; }
"""


def generate_report(results: list[dict], output_path: str = "eval_report.html") -> str:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    model = "claude-opus-4-1"

    scenario_cards = "\n".join(_scenario_card(r, i) for i, r in enumerate(results))

    html_doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Personal Finance Agent — Eval Report</title>
<style>{CSS}</style>
</head>
<body>
<h1>Personal Finance Agent — Eval Report</h1>
<p class="subtitle">Model: <strong>{_esc(model)}</strong> &nbsp;|&nbsp; Generated: {_esc(timestamp)}</p>

<div class="card">
  <h2>Summary</h2>
  {_summary_table(results)}
  <h2 style="margin-top:24px;">Aggregate</h2>
  {_aggregate(results)}
</div>

{scenario_cards}
</body>
</html>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_doc)

    return output_path
