document.addEventListener('DOMContentLoaded', () => {
  // DOM Elements
  const dropZone = document.getElementById('dropZone');
  const fileInput = document.getElementById('fileInput');
  const filePreviewContainer = document.getElementById('filePreviewContainer');
  const modeCards = document.querySelectorAll('.mode-card');
  const processBtn = document.getElementById('processBtn');
  const resultsSection = document.getElementById('resultsSection');
  const resultsContainer = document.getElementById('resultsContainer');
  const globalStatus = document.getElementById('globalStatus');
  
  // Modal Elements
  const imageModal = document.getElementById('imageModal');
  const closeModalBtn = document.querySelector('.close-modal');
  const comparisonSlider = document.getElementById('comparisonSlider');
  const sliderHandle = document.querySelector('.slider-handle');
  const afterImgWrapper = document.querySelector('.img-wrapper.after');
  const modalBeforeImg = document.getElementById('modalBeforeImg');
  const modalAfterImg = document.getElementById('modalAfterImg');
  const modalJsonLog = document.getElementById('modalJsonLog');

  // Settings Elements
  const settingsBtn = document.getElementById('settingsBtn');
  const settingsModal = document.getElementById('settingsModal');
  const closeSettingsBtn = document.querySelector('.close-settings');
  const saveSettingsBtn = document.getElementById('saveSettingsBtn');
  const grokApiKeyInput = document.getElementById('grokApiKeyInput');

  // Initialization
  const savedKey = localStorage.getItem('grok_api_key');
  if (savedKey) grokApiKeyInput.value = savedKey;
  
  let selectedFiles = [];

  // --- Settings Modal Handling ---
  settingsBtn.addEventListener('click', () => {
    settingsModal.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
  });

  function closeSettings() {
    settingsModal.classList.add('hidden');
    document.body.style.overflow = '';
  }

  closeSettingsBtn.addEventListener('click', closeSettings);
  settingsModal.addEventListener('click', (e) => {
    if (e.target === settingsModal) closeSettings();
  });

  saveSettingsBtn.addEventListener('click', () => {
    const key = grokApiKeyInput.value.trim();
    if (key) {
      localStorage.setItem('grok_api_key', key);
      alert('Grok API Key saved locally!');
      closeSettings();
    } else {
      localStorage.removeItem('grok_api_key');
      alert('Key removed.');
      closeSettings();
    }
  });

  // --- 1. Mode Selection ---
  modeCards.forEach(card => {
    card.addEventListener('click', () => {
      // Remove active class from all
      modeCards.forEach(c => c.classList.remove('active'));
      // Add active class to clicked
      card.classList.add('active');
    });
  });

  // --- 2. File Upload Handling ---
  dropZone.addEventListener('click', () => fileInput.click());

  dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('dragover');
  });

  dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('dragover');
  });

  dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    if (e.dataTransfer.files.length > 0) {
      handleFiles(e.dataTransfer.files);
    }
  });

  fileInput.addEventListener('change', () => {
    if (fileInput.files.length > 0) {
      handleFiles(fileInput.files);
    }
  });

  function handleFiles(files) {
    const validTypes = ['image/jpeg', 'image/png'];
    const newFiles = Array.from(files).filter(file => validTypes.includes(file.type));
    
    if (newFiles.length === 0) {
      alert('Please upload JPEG or PNG images only.');
      return;
    }

    selectedFiles = [...selectedFiles, ...newFiles];
    updateFilePreviews();
    
    // Enable process button if we have files
    if (selectedFiles.length > 0) {
      processBtn.removeAttribute('disabled');
    }
  }

  function updateFilePreviews() {
    // Hide text, show previews
    Array.from(dropZone.children).forEach(child => {
      if (!child.classList.contains('preview-grid') && child.tagName !== 'INPUT') {
        child.classList.add('hidden');
      }
    });
    
    filePreviewContainer.classList.remove('hidden');
    filePreviewContainer.innerHTML = '';
    
    selectedFiles.forEach((file) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        const item = document.createElement('div');
        item.className = 'preview-item';
        item.innerHTML = `<img src="${e.target.result}" alt="Preview">`;
        filePreviewContainer.appendChild(item);
      };
      reader.readAsDataURL(file);
    });
  }

  // --- 3. API Processing ---
  processBtn.addEventListener('click', async () => {
    if (selectedFiles.length === 0) return;
    
    const apiKey = grokApiKeyInput.value.trim();
    if (!apiKey) {
      alert('Please configure your Grok API Key in Settings first.');
      settingsModal.classList.remove('hidden');
      return;
    }
    
    // Get selected mode
    const selectedMode = document.querySelector('input[name="mode"]:checked').value;
    
    // UI Updates
    processBtn.setAttribute('disabled', 'true');
    processBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> <span>Processing...</span>';
    
    resultsSection.classList.remove('hidden');
    globalStatus.className = 'status-badge processing';
    globalStatus.textContent = 'Processing...';
    resultsContainer.innerHTML = ''; // Clear old results

    // Process files sequentially (one request per file — multer.single)
    const sessionFolder = 'lumina_' + Date.now();
    const allResults = [];

    try {
      for (const file of selectedFiles) {
        const fd = new FormData();
        fd.append('image', file);          // singular 'image' — matches multer.single('image')
        fd.append('mode', selectedMode);
        fd.append('apiKey', apiKey);
        fd.append('sessionFolder', sessionFolder);

        const response = await fetch('/api/process-image', { method: 'POST', body: fd });
        const data = await response.json();
        if (data.success) {
          allResults.push(data);
        } else {
          console.warn('File failed:', file.name, data.error);
        }
      }

      if (allResults.length > 0) {
        displayResults(allResults);
        globalStatus.className = 'status-badge completed';
        globalStatus.textContent = `Done (${allResults.length}/${selectedFiles.length})`;
      } else {
        throw new Error('All files failed to process');
      }
    } catch (error) {
      console.error('Processing error:', error);
      alert('An error occurred during processing: ' + error.message);
      globalStatus.className = 'status-badge processing';
      globalStatus.textContent = 'Failed';
      globalStatus.style.background = 'rgba(255, 0, 0, 0.2)';
      globalStatus.style.color = '#ff4d4d';
    } finally {
      processBtn.removeAttribute('disabled');
      processBtn.innerHTML = '<span>Process Photos</span><i class="fa-solid fa-arrow-right"></i>';
      // Clear queue
      selectedFiles = [];
      fileInput.value = '';
      
      // Reset dropzone
      setTimeout(() => {
        filePreviewContainer.innerHTML = '';
        filePreviewContainer.classList.add('hidden');
        Array.from(dropZone.children).forEach(child => {
          if (!child.classList.contains('preview-grid') && child.tagName !== 'INPUT') {
            child.classList.remove('hidden');
          }
        });
      }, 1000);
    }
  });

  function displayResults(results) {
    results.forEach((result, index) => {
      const card = document.createElement('div');
      card.className = 'result-card fade-in';
      card.style.animationDelay = `${index * 0.1}s`;

      // Bug fix: server returns resultUrl (not processedUrl)
      const resultUrl   = result.resultUrl   || '';
      const originalUrl = result.originalUrl || resultUrl;
      const modeLabel   = resultUrl.includes('_empty') ? 'Full Empty' : 'Clean & Stage';
      const session     = (result.sessionFolder || '').replace(/_/g, ' ');

      // Build card using DOM to avoid XSS
      const imgWrapper = document.createElement('div');
      imgWrapper.className = 'result-img-wrapper';
      imgWrapper.dataset.before = originalUrl;
      imgWrapper.dataset.after  = resultUrl;

      const img = document.createElement('img');
      img.src = resultUrl;
      img.alt = 'Processed Result';
      imgWrapper.appendChild(img);

      const info = document.createElement('div');
      info.className = 'result-info';
      const roomSpan = document.createElement('span');
      roomSpan.className = 'room-type';
      roomSpan.textContent = session;
      const modeH4 = document.createElement('h4');
      modeH4.textContent = modeLabel;
      info.appendChild(roomSpan);
      info.appendChild(modeH4);

      card.appendChild(imgWrapper);
      card.appendChild(info);

      imgWrapper.addEventListener('click', function() {
        openModal(this.dataset.before, this.dataset.after, {});
      });

      resultsContainer.appendChild(card);
    });
  }

  // --- 4. Modal and Slider Logic ---
  function openModal(beforeSrc, afterSrc, logData) {
    modalBeforeImg.src = beforeSrc;
    modalAfterImg.src = afterSrc;
    
    // Format JSON with 2 spaces
    modalJsonLog.textContent = JSON.stringify(logData, null, 2);
    
    // Reset slider
    comparisonSlider.value = 50;
    updateSlider(50);
    
    imageModal.classList.remove('hidden');
    document.body.style.overflow = 'hidden'; // Prevent background scrolling
  }

  function closeModal() {
    imageModal.classList.add('hidden');
    document.body.style.overflow = '';
  }

  closeModalBtn.addEventListener('click', closeModal);
  
  // Close modal on background click
  imageModal.addEventListener('click', (e) => {
    if (e.target === imageModal) {
      closeModal();
    }
  });

  // Handle Slider
  function updateSlider(val) {
    afterImgWrapper.style.clipPath = `inset(0 ${100 - val}% 0 0)`;
    sliderHandle.style.left = `${val}%`;
  }

  comparisonSlider.addEventListener('input', (e) => {
    updateSlider(e.target.value);
  });
  
});

// Simple CSS animation injection for fade-in
const style = document.createElement('style');
style.textContent = `
  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
  }
  .fade-in {
    animation: fadeIn 0.5s ease forwards;
    opacity: 0;
  }
`;
document.head.appendChild(style);
