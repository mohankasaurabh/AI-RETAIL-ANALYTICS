// =====================================================
// Core API helper — thin fetch wrapper
// =====================================================
// Usage: const data = await API.get('/api/dashboard');
//        await API.post('/api/sources/1/start');

window.API = {
    async get(url) {
        const r = await fetch(url);
        if (!r.ok) throw new Error(`GET ${url} -> ${r.status}`);
        return r.json();
    },

    async post(url, body) {
        const r = await fetch(url, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: body ? JSON.stringify(body) : undefined,
        });
        if (!r.ok) throw new Error(`POST ${url} -> ${r.status}`);
        return r.json();
    },

    async put(url, body) {
        const r = await fetch(url, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body || {}),
        });
        if (!r.ok) throw new Error(`PUT ${url} -> ${r.status}`);
        return r.json();
    },

    async del(url) {
        const r = await fetch(url, { method: "DELETE" });
        if (!r.ok) throw new Error(`DELETE ${url} -> ${r.status}`);
        return r.json();
    },
};
