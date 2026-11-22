// Authored by Claude Sonnet
// Find every element with class "gallery" that also has a data-folder attribute.
// (So a page can even have several galleries, each pointing at its own folder.)
document.querySelectorAll('.gallery[data-folder]').forEach(async (gallery) => {

    // Read the folder from data-folder, and strip a trailing "/" if there is one
    // so we don't end up with "folder//file.jpg".
    const folder = gallery.dataset.folder.replace(/\/$/, '');

    try {
        // Download the manifest (the list of filenames) from that folder.
        const res = await fetch(`${folder}/manifest.json`);

        // fetch doesn't throw on a 404, so check manually and bail out if it failed.
        if (!res.ok) throw new Error(`HTTP ${res.status}`);

        // Parse the JSON into an array like [{file: "a.jpg", alt: "..."}, ...]
        const items = await res.json();

        // Build one <figure><img></figure> per entry in the manifest.
        for (const item of items) {
            const figure = document.createElement('figure');
            const img = document.createElement('img');

            // encodeURIComponent protects against spaces or odd characters in filenames.
            img.src = `${folder}/${encodeURIComponent(item.file)}`;
            img.alt = item.alt || '';     // alt text for accessibility; empty if not provided
            img.dataset.camera = item.camera || '';   // stored on the element so the lightbox can read it
            img.dataset.caption = item.caption || '';
            img.loading = 'lazy';         // only load images as they scroll into view

            figure.append(img);           // put the image inside the figure
            gallery.append(figure);       // put the figure inside the gallery grid
        }
    } catch (err) {
        // If anything goes wrong, report it in the browser console (F12 > Console)
        // instead of silently showing an empty page.
        console.error(`Could not load gallery from ${folder}:`, err);
    }
});

// Build the popup once: an image plus a caption area underneath.
const lightbox = document.createElement('dialog');
lightbox.className = 'lightbox';

const bigImg = document.createElement('img');
const caption = document.createElement('div');
caption.className = 'lightbox__caption';
const captionAlt = document.createElement('p');      // the alt text, used as a caption
const captionCamera = document.createElement('p');   // the camera name
captionCamera.className = 'lightbox__camera';
caption.append(captionAlt, captionCamera);

lightbox.append(bigImg, caption);
document.body.append(lightbox);

document.addEventListener('click', (event) => {
    const img = event.target.closest('.gallery img');
    if (!img) return;

    bigImg.src = img.src;
    bigImg.alt = img.alt;
    // textContent (not innerHTML) so odd characters in the text can't be treated as HTML
    captionAlt.textContent = img.dataset.caption || img.alt;
    captionCamera.textContent = img.dataset.camera ? `${img.dataset.camera}` : '';
    lightbox.showModal();
});

lightbox.addEventListener('click', () => lightbox.close());