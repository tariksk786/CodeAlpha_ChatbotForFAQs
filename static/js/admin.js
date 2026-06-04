/**
 * Admin Panel Javascript for managing FAQs
 * Handles FAQ CRUD APIs, searching, paginated tables, and CSV/JSON bulk uploads.
 */

document.addEventListener('DOMContentLoaded', () => {
    // State management
    let currentPage = 1;
    const itemsPerPage = 8;
    let totalItems = 0;
    let faqList = [];
    let categoriesList = [];

    // DOM Elements
    const faqTableBody = document.getElementById('faq-table-body');
    const searchInput = document.getElementById('faq-search');
    const categoryFilter = document.getElementById('faq-category-filter');
    const paginationContainer = document.getElementById('pagination-container');
    const totalCountText = document.getElementById('total-faqs-count');
    
    // Modal Form Elements
    const faqModalElement = document.getElementById('faqModal');
    const faqForm = document.getElementById('faq-form');
    const modalTitle = document.getElementById('faqModalLabel');
    const faqIdInput = document.getElementById('faq-id');
    const questionInput = document.getElementById('faq-question');
    const answerInput = document.getElementById('faq-answer');
    const categoryInput = document.getElementById('faq-category');
    
    // Import File Elements
    const importFileInput = document.getElementById('import-file');
    const btnImport = document.getElementById('btn-import');

    // Initialize BootStrap Modal object if exists
    let faqModal = null;
    if (faqModalElement && window.bootstrap) {
        faqModal = new bootstrap.Modal(faqModalElement);
    }

    // Load initial data
    loadFAQs();

    // Event Listeners
    if (searchInput) {
        // Debounce search input to prevent rapid api querying
        let searchTimeout;
        searchInput.addEventListener('input', () => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                currentPage = 1;
                loadFAQs();
            }, 300);
        });
    }

    if (categoryFilter) {
        categoryFilter.addEventListener('change', () => {
            currentPage = 1;
            loadFAQs();
        });
    }

    if (faqForm) {
        faqForm.addEventListener('submit', handleFormSubmit);
    }

    if (btnImport && importFileInput) {
        btnImport.addEventListener('click', handleBulkImport);
    }

    // Load FAQs via API
    function loadFAQs() {
        const query = searchInput ? searchInput.value.trim() : '';
        const cat = categoryFilter ? categoryFilter.value : '';
        const offset = (currentPage - 1) * itemsPerPage;
        
        let url = `/api/faqs?limit=${itemsPerPage}&offset=${offset}`;
        if (query) url += `&search=${encodeURIComponent(query)}`;
        if (cat) url += `&category=${encodeURIComponent(cat)}`;

        // Show table loaders skeleton
        showTableLoadingState();

        fetch(url)
            .then(res => {
                if (!res.ok) throw new Error("HTTP error " + res.status);
                return res.json();
            })
            .then(data => {
                faqList = data.faqs;
                totalItems = data.total;
                categoriesList = data.categories;
                
                renderTable();
                renderPagination();
                updateCategoryFilters();
                
                if (totalCountText) {
                    totalCountText.innerText = totalItems;
                }
            })
            .catch(err => {
                console.error("Error loading FAQs:", err);
                if (faqTableBody) {
                    faqTableBody.innerHTML = `
                        <tr>
                            <td colspan="5" class="text-center text-danger py-4">
                                <i class="fas fa-exclamation-triangle me-2"></i> Failed to load FAQs from database.
                            </td>
                        </tr>
                    `;
                }
            });
    }

    // Show skeletal loader in table body
    function showTableLoadingState() {
        if (!faqTableBody) return;
        faqTableBody.innerHTML = '';
        for (let i = 0; i < 4; i++) {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><div class="skeleton-box" style="width: 30px;"></div></td>
                <td><div class="skeleton-box" style="width: 80px;"></div></td>
                <td><div class="skeleton-box"></div></td>
                <td><div class="skeleton-box"></div></td>
                <td><div class="skeleton-box" style="width: 80px;"></div></td>
            `;
            faqTableBody.appendChild(tr);
        }
    }

    // Render FAQ rows
    function renderTable() {
        if (!faqTableBody) return;
        faqTableBody.innerHTML = '';

        if (faqList.length === 0) {
            faqTableBody.innerHTML = `
                <tr>
                    <td colspan="5" class="text-center text-muted py-4">
                        <i class="fas fa-inbox me-2"></i> No FAQ records found.
                    </td>
                </tr>
            `;
            return;
        }

        faqList.forEach((faq, index) => {
            const tr = document.createElement('tr');
            const rowNumber = (currentPage - 1) * itemsPerPage + index + 1;
            
            // Limit answer size for table presentation
            const shortAnswer = faq.answer.length > 80 ? faq.answer.slice(0, 80) + '...' : faq.answer;
            
            tr.innerHTML = `
                <td>${rowNumber}</td>
                <td><span class="category-badge">${escapeHtml(faq.category)}</span></td>
                <td><strong>${escapeHtml(faq.question)}</strong></td>
                <td>${escapeHtml(shortAnswer)}</td>
                <td>
                    <button class="btn btn-sm btn-outline-info btn-edit me-1" data-id="${faq.id}">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger btn-delete" data-id="${faq.id}">
                        <i class="fas fa-trash-alt"></i>
                    </button>
                </td>
            `;

            // Attach event listeners
            tr.querySelector('.btn-edit').addEventListener('click', () => showEditModal(faq));
            tr.querySelector('.btn-delete').addEventListener('click', () => confirmDeleteFAQ(faq.id));

            faqTableBody.appendChild(tr);
        });
    }

    // Render pagination controls
    function renderPagination() {
        if (!paginationContainer) return;
        paginationContainer.innerHTML = '';

        const totalPages = Math.ceil(totalItems / itemsPerPage);
        if (totalPages <= 1) return;

        // Previous button
        const prevBtn = document.createElement('button');
        prevBtn.className = 'btn-pagination';
        prevBtn.innerHTML = '<i class="fas fa-chevron-left"></i>';
        prevBtn.disabled = currentPage === 1;
        prevBtn.addEventListener('click', () => {
            currentPage--;
            loadFAQs();
        });
        paginationContainer.appendChild(prevBtn);

        // Page numbers
        for (let i = 1; i <= totalPages; i++) {
            const pageBtn = document.createElement('button');
            pageBtn.className = `btn-pagination ${i === currentPage ? 'active' : ''}`;
            pageBtn.innerText = i;
            pageBtn.addEventListener('click', () => {
                currentPage = i;
                loadFAQs();
            });
            paginationContainer.appendChild(pageBtn);
        }

        // Next button
        const nextBtn = document.createElement('button');
        nextBtn.className = 'btn-pagination';
        nextBtn.innerHTML = '<i class="fas fa-chevron-right"></i>';
        nextBtn.disabled = currentPage === totalPages;
        nextBtn.addEventListener('click', () => {
            currentPage++;
            loadFAQs();
        });
        paginationContainer.appendChild(nextBtn);
    }

    // Sync categories dropdown filters
    function updateCategoryFilters() {
        if (!categoryFilter) return;
        
        const currentValue = categoryFilter.value;
        
        // Clear all except "All Categories"
        categoryFilter.innerHTML = '<option value="">All Categories</option>';
        
        categoriesList.forEach(cat => {
            const opt = document.createElement('option');
            opt.value = cat;
            opt.innerText = cat;
            if (cat === currentValue) {
                opt.selected = true;
            }
            categoryFilter.appendChild(opt);
        });
    }

    // HTML escape utility
    function escapeHtml(text) {
        if (!text) return '';
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, function(m) { return map[m]; });
    }

    // Show add modal trigger
    const btnAddFaq = document.getElementById('btn-add-faq');
    if (btnAddFaq) {
        btnAddFaq.addEventListener('click', () => {
            if (faqForm) faqForm.reset();
            if (faqIdInput) faqIdInput.value = '';
            if (modalTitle) modalTitle.innerText = 'Add New FAQ';
            if (faqModal) faqModal.show();
        });
    }

    // Show edit modal trigger
    function showEditModal(faq) {
        if (modalTitle) modalTitle.innerText = 'Edit FAQ';
        if (faqIdInput) faqIdInput.value = faq.id;
        if (questionInput) questionInput.value = faq.question;
        if (answerInput) answerInput.value = faq.answer;
        if (categoryInput) categoryInput.value = faq.category;
        
        if (faqModal) faqModal.show();
    }

    // Form Submit (Add or Edit FAQ)
    function handleFormSubmit(e) {
        e.preventDefault();
        
        const faqId = faqIdInput ? faqIdInput.value : '';
        const question = questionInput ? questionInput.value.trim() : '';
        const answer = answerInput ? answerInput.value.trim() : '';
        const category = categoryInput ? categoryInput.value.trim() : 'General';

        if (!question || !answer) {
            Swal.fire("Validation Error", "Question and Answer fields are required.", "error");
            return;
        }

        const isEdit = faqId !== '';
        const url = isEdit ? `/api/faqs/update/${faqId}` : '/api/faqs/add';
        const method = isEdit ? 'PUT' : 'POST';

        fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question, answer, category })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                if (faqModal) faqModal.hide();
                loadFAQs();
                Swal.fire({
                    title: 'Saved!',
                    text: data.message,
                    icon: 'success',
                    timer: 1500,
                    showConfirmButton: false
                });
            } else {
                Swal.fire("Operation Failed", data.error, "error");
            }
        })
        .catch(err => {
            console.error("Form submit error:", err);
            Swal.fire("Network Error", "Failed to communicate with database.", "error");
        });
    }

    // Confirm FAQ delete
    function confirmDeleteFAQ(faqId) {
        Swal.fire({
            title: 'Delete this FAQ?',
            text: "This FAQ will be removed permanently. The AI matcher will immediately reindex.",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#EF4444',
            cancelButtonColor: '#1e293b',
            confirmButtonText: 'Yes, delete it!'
        }).then((result) => {
            if (result.isConfirmed) {
                fetch(`/api/faqs/delete/${faqId}`, { method: 'DELETE' })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        loadFAQs();
                        Swal.fire({
                            title: 'Deleted!',
                            text: data.message,
                            icon: 'success',
                            timer: 1500,
                            showConfirmButton: false
                        });
                    } else {
                        Swal.fire("Error", data.error, "error");
                    }
                })
                .catch(err => {
                    console.error("Delete error:", err);
                    Swal.fire("Network Error", "Could not complete FAQ deletion.", "error");
                });
            }
        });
    }

    // Bulk Import logic
    function handleBulkImport() {
        if (!importFileInput || !importFileInput.files || importFileInput.files.length === 0) {
            Swal.fire("No file", "Please select a valid CSV or JSON file first.", "info");
            return;
        }

        const file = importFileInput.files[0];
        const formData = new FormData();
        formData.append('file', file);

        Swal.fire({
            title: 'Importing FAQs...',
            text: 'Parsing file contents and rebuilding vectors.',
            allowOutsideClick: false,
            didOpen: () => {
                Swal.showLoading();
            }
        });

        fetch('/api/faqs/import', {
            method: 'POST',
            body: formData
        })
        .then(res => res.json())
        .then(data => {
            Swal.close();
            if (data.success) {
                importFileInput.value = ''; // clear input
                loadFAQs();
                Swal.fire("Import Complete", data.message, "success");
            } else {
                Swal.fire("Import Failed", data.error || data.details, "error");
            }
        })
        .catch(err => {
            Swal.close();
            console.error("Import error:", err);
            Swal.fire("Network Error", "Could not complete bulk import request.", "error");
        });
    }
});
