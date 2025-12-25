// File upload functionality for Tenant Registration
// Scoped to elements on daftartenantinkubator.html
(function () {
  document.addEventListener('DOMContentLoaded', function () {
    var fileInput = document.getElementById('form_upload');
    if (!fileInput) return;

    var fileLabel = document.querySelector('.file-label');
    var fileText = document.querySelector('.file-text');
    var fileIcon = document.querySelector('.file-label i');

    function resetUI() {
      if (!fileLabel) return;
      fileLabel.classList.remove('file-selected');
      if (fileIcon) fileIcon.className = 'fas fa-cloud-upload-alt';
      if (fileText) fileText.textContent = 'Pilih file atau drag & drop di sini';
    }

    fileInput.addEventListener('change', function (e) {
      var file = e.target.files[0];
      if (file) {
        if (file.size > 5 * 1024 * 1024) {
          alert('File terlalu besar! Maksimal 5MB.');
          fileInput.value = '';
          resetUI();
          return;
        }
        if (fileLabel) fileLabel.classList.add('file-selected');
        if (fileIcon) fileIcon.className = 'fas fa-check-circle';
        if (fileText) fileText.textContent = 'File terpilih: ' + file.name;
      } else {
        resetUI();
      }
    });

    if (fileLabel) {
      fileLabel.addEventListener('dragover', function (e) {
        e.preventDefault();
        fileLabel.style.borderColor = '#2980b9';
        fileLabel.style.background = '#e3f2fd';
      });

      fileLabel.addEventListener('dragleave', function (e) {
        e.preventDefault();
        fileLabel.style.borderColor = '#3498db';
        fileLabel.style.background = '#f8f9fa';
      });

      fileLabel.addEventListener('drop', function (e) {
        e.preventDefault();
        fileLabel.style.borderColor = '#3498db';
        fileLabel.style.background = '#f8f9fa';
        var files = e.dataTransfer.files;
        if (files && files.length > 0) {
          fileInput.files = files;
          fileInput.dispatchEvent(new Event('change'));
        }
      });
    }
  });
})();
