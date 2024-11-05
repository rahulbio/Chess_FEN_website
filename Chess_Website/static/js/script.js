document.addEventListener('DOMContentLoaded', function() {
    // Preview uploaded image
    const fileInput = document.getElementById('file');
    const previewContainer = document.getElementById('preview-container');
    
    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    previewContainer.innerHTML = `
                        <img src="${e.target.result}" class="preview-image" alt="Preview">
                    `;
                }
                reader.readAsDataURL(file);
            }
        });
    }
});