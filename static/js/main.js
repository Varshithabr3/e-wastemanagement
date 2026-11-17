// Main Client-Side JavaScript
document.addEventListener('DOMContentLoaded', function () {
  // 1. Bootstrap Form Validation
  const forms = document.querySelectorAll('.needs-validation');
  Array.from(forms).forEach(function (form) {
    form.addEventListener('submit', function (event) {
      if (!form.checkValidity()) {
        event.preventDefault();
        event.stopPropagation();
      }
      form.classList.add('was-validated');
    }, false);
  });

  // 2. Image Upload Preview
  const imageInput = document.getElementById('imageUploadInput');
  const imagePreviewContainer = document.getElementById('imagePreviewContainer');
  const imagePreview = document.getElementById('imagePreview');

  if (imageInput && imagePreviewContainer && imagePreview) {
    imageInput.addEventListener('change', function () {
      const file = this.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
          imagePreview.src = e.target.result;
          imagePreviewContainer.classList.remove('d-none');
        };
        reader.readAsDataURL(file);
      } else {
        imagePreview.src = '#';
        imagePreviewContainer.classList.add('d-none');
      }
    });
  }

  // 3. Auto-Dismiss Flash Alerts after 5 seconds
  const alertElements = document.querySelectorAll('.alert-dismissible');
  alertElements.forEach(function (alert) {
    setTimeout(function () {
      try {
        const bsAlert = new bootstrap.Alert(alert);
        bsAlert.close();
      } catch (e) {
        // fallback
        alert.style.display = 'none';
      }
    }, 5500);
  });

  // 4. Multi-Select Counter for Collection Request Items
  const itemCheckboxes = document.querySelectorAll('.ewaste-select-checkbox');
  const selectedCountBadge = document.getElementById('selectedItemsCount');
  const submitRequestBtn = document.getElementById('btnSubmitRequest');

  if (itemCheckboxes.length > 0 && selectedCountBadge) {
    function updateSelectedCount() {
      const checkedCount = document.querySelectorAll('.ewaste-select-checkbox:checked').length;
      selectedCountBadge.textContent = checkedCount;
      if (submitRequestBtn) {
        submitRequestBtn.disabled = checkedCount === 0;
      }
    }
    itemCheckboxes.forEach(cb => cb.addEventListener('change', updateSelectedCount));
    updateSelectedCount();
  }

  // 5. Select All Items Checkbox
  const selectAllCheckbox = document.getElementById('selectAllItems');
  if (selectAllCheckbox && itemCheckboxes.length > 0) {
    selectAllCheckbox.addEventListener('change', function () {
      itemCheckboxes.forEach(cb => {
        cb.checked = selectAllCheckbox.checked;
      });
      if (selectedCountBadge) {
        const checkedCount = document.querySelectorAll('.ewaste-select-checkbox:checked').length;
        selectedCountBadge.textContent = checkedCount;
        if (submitRequestBtn) submitRequestBtn.disabled = checkedCount === 0;
      }
    });
  }

  // 6. Initialize Bootstrap Tooltips
  const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });
});

