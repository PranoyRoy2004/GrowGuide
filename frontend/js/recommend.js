// frontend/js/recommend.js

const API = "http://127.0.0.1:5000";

// ── Tab switching ─────────────────────────────────────────────
function switchTab(tab) {
    document.getElementById("tab-natural").style.display = tab === "natural" ? "block" : "none";
    document.getElementById("tab-manual").style.display  = tab === "manual"  ? "block" : "none";
    document.querySelectorAll(".tab-btn").forEach((b, i) => {
        b.classList.toggle("active", (tab === "natural" && i === 0) || (tab === "manual" && i === 1));
    });
    hideResult();
}

// ── Show/hide result ──────────────────────────────────────────
function showResult(data) {
    const box = document.getElementById("result-box");

    document.getElementById("result-crop").textContent = data.top_crop;
    document.getElementById("result-confidence").textContent =
        `Confidence: ${data.confidence}%`;

    // Render top-3 bars
    const barsEl = document.getElementById("result-bars");
    barsEl.innerHTML = data.top_3.map(item => `
        <div class="crop-bar">
            <div class="crop-label">
                <span>${item.crop}</span>
                <span>${item.confidence}%</span>
            </div>
            <div class="bar-track">
                <div class="bar-fill" style="width:${item.confidence}%"></div>
            </div>
        </div>
    `).join("");

    box.classList.add("show");
    box.scrollIntoView({ behavior: "smooth", block: "start" });
}

function hideResult() {
    document.getElementById("result-box").classList.remove("show");
}

// ── Set button loading state ──────────────────────────────────
function setLoading(btnId, loading) {
    const btn = document.getElementById(btnId);
    btn.disabled = loading;
    btn.innerHTML = loading
        ? `<span class="spinner"></span> Processing...`
        : btn.id === "nl-btn"
            ? "🔍 Analyse & Recommend"
            : "🌿 Get Recommendation";
}

function showError(elId, msg) {
    const el = document.getElementById(elId);
    el.textContent = msg;
    el.classList.add("show");
    setTimeout(() => el.classList.remove("show"), 5000);
}

// ── Natural Language handler ──────────────────────────────────
async function handleNaturalLanguage() {
    const text = document.getElementById("nl-input").value.trim();

    if (text.length < 10) {
        showError("nl-error", "Please enter a more detailed description of your farm.");
        return;
    }

    setLoading("nl-btn", true);
    hideResult();
    document.getElementById("nl-features").style.display = "none";

    try {
        const res = await fetch(`${API}/parse-input`, {
            method : "POST",
            headers: { "Content-Type": "application/json" },
            body   : JSON.stringify({ text, recommend: true })
        });

        const data = await res.json();

        if (!data.success) {
            showError("nl-error", data.error || "Something went wrong.");
            return;
        }

        // Show extracted features
        const featuresGrid = document.getElementById("nl-features-grid");
        const labels = { N:"Nitrogen", P:"Phosphorus", K:"Potassium",
                         temperature:"Temp °C", humidity:"Humidity %",
                         ph:"Soil pH", rainfall:"Rainfall mm" };

        featuresGrid.innerHTML = Object.entries(data.extracted_features)
            .map(([k, v]) => `
                <div class="feature-chip">
                    <div class="chip-label">${labels[k] || k}</div>
                    <div class="chip-value">${parseFloat(v).toFixed(1)}</div>
                </div>
            `).join("");

        document.getElementById("nl-method").textContent = data.extraction_method;
        document.getElementById("nl-features").style.display = "block";

        // Show recommendation
        if (data.recommendation) {
            showResult(data.recommendation);
        }

    } catch (err) {
        showError("nl-error", "Cannot connect to server. Make sure Flask is running.");
    } finally {
        setLoading("nl-btn", false);
    }
}

// ── Manual input handler ──────────────────────────────────────
async function handleManual() {
    const fields = ["m-N","m-P","m-K","m-temp","m-humidity","m-ph","m-rainfall"];
    const keys   = ["N","P","K","temperature","humidity","ph","rainfall"];
    const payload = {};

    for (let i = 0; i < fields.length; i++) {
        const val = document.getElementById(fields[i]).value.trim();
        if (val === "") {
            showError("manual-error", "Please fill in all fields.");
            return;
        }
        payload[keys[i]] = parseFloat(val);
    }

    setLoading("manual-btn", true);
    hideResult();

    try {
        const res = await fetch(`${API}/recommend-crop`, {
            method : "POST",
            headers: { "Content-Type": "application/json" },
            body   : JSON.stringify(payload)
        });

        const data = await res.json();

        if (!data.success) {
            showError("manual-error", data.error || "Something went wrong.");
            return;
        }

        showResult(data);

    } catch (err) {
        showError("manual-error", "Cannot connect to server. Make sure Flask is running.");
    } finally {
        setLoading("manual-btn", false);
    }
}