document.querySelectorAll("[data-tab-target]").forEach((button) => {
    button.addEventListener("click", () => {
        const target = button.getAttribute("data-tab-target");
        document.querySelectorAll("[data-tab-target]").forEach((item) => item.classList.remove("active"));
        document.querySelectorAll(".tab-panel").forEach((panel) => panel.classList.remove("active"));
        button.classList.add("active");
        document.querySelector(target).classList.add("active");
    });
});

const htmlEscapeMap = {
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;",
};

function escapeHtml(value) {
    return value.replace(/[&<>"']/g, (char) => htmlEscapeMap[char]);
}

function tokenClass(token) {
    if (token.startsWith("#") || token.startsWith("//")) return "comment";
    if (token.startsWith('"') || token.startsWith("'") || token.startsWith("`")) return "string";
    if (token.startsWith("@")) return "decorator";
    if (/^\d/.test(token)) return "number";
    if (/^[A-Za-z_][A-Za-z0-9_]*(?=\()/.test(token)) return "function";
    return "keyword";
}

function highlightCodeBlock(code) {
    const source = code.textContent;
    const tokenPattern = /#[^\n]*|\/\/[^\n]*|"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|`(?:\\.|[^`\\])*`|@[A-Za-z_][\w.]*|\b(?:from|import|def|class|async|await|return|if|elif|else|for|while|with|as|try|except|raise|pass|None|True|False|in|is|not|and|or|yield|lambda|match|case|with|open|curl|docker|alembic|uvicorn|pytest|pip|cd|GET|POST|PUT|DELETE|PATCH|FastAPI|Depends|HTTPException|BaseModel|SQLModel|Field|AsyncSession|Session|Column|Relationship|JSON|Header|Request|Response)\b|\b\d+(?:\.\d+)?\b|\b[A-Za-z_][A-Za-z0-9_]*(?=\()/g;
    let result = "";
    let cursor = 0;
    let match = tokenPattern.exec(source);

    while (match !== null) {
        const token = match[0];
        result += escapeHtml(source.slice(cursor, match.index));
        result += `<span class="syntax-token ${tokenClass(token)}">${escapeHtml(token)}</span>`;
        cursor = match.index + token.length;
        match = tokenPattern.exec(source);
    }

    result += escapeHtml(source.slice(cursor));
    code.innerHTML = result;
    code.classList.add("syntax-highlighted");
}

function highlightCodeBlocks() {
    document.querySelectorAll("pre code").forEach((code) => {
        if (!code.classList.contains("syntax-highlighted")) {
            highlightCodeBlock(code);
        }
    });
}

highlightCodeBlocks();
