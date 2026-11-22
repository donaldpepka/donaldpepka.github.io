// Authored by Claude Sonnet

// For each album link, load its folder's manifest and use the cover photo.
document.querySelectorAll('.album[data-folder]').forEach(async (album) => {
    const folder = album.dataset.folder.replace(/\/$/, '');

    try {
        const res = await fetch(`${folder}/manifest.json`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const items = await res.json();

        // Prefer the entry flagged "cover": true; otherwise use the first photo.
        const cover = items.find(item => item.cover) || items[0];

        const img = album.querySelector('img');
        img.src = `${folder}/${encodeURIComponent(cover.file)}`;
        // alt stays empty on purpose: the <span> title already names the link,
        // and an image with alt text would make screen readers say it twice.
    } catch (err) {
        console.error(`Could not load cover for ${folder}:`, err);
    }
});