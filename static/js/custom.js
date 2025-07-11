document.addEventListener('DOMContentLoaded', () => {
    // 模態框 ID 清單
    const modalIds = ['loginModal', 'registerModal'];

    // 通用模態框事件處理
    const handleModalBackdrop = (addClass) => {
        const backdrop = document.querySelector('.modal-backdrop');
        if (backdrop) {
            backdrop.classList.toggle('custom-bg', addClass);
        }
    };

    // 全局模態框事件
    document.addEventListener('show.bs.modal', () => handleModalBackdrop(true));
    document.addEventListener('hidden.bs.modal', () => handleModalBackdrop(false));

    // 為 AJAX 載入的模態框綁定事件
    modalIds.forEach(modalId => {
        const modalElement = document.getElementById(modalId);
        if (modalElement) {
            modalElement.addEventListener('show.bs.modal', () => handleModalBackdrop(true));
        }
    });
});