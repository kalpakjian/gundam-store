document.addEventListener('DOMContentLoaded', () => {
    // 更新年份
    const date = new Date();
    const yearElement = document.querySelector('.year');
    if (yearElement) {
        yearElement.innerHTML = date.getFullYear();
    }

    // 訊息淡出
    const messageElement = document.querySelector('#message');
    if (messageElement) {
        setTimeout(() => {
            messageElement.style.display = 'none';
        }, 4000); // 等待 3s + 1s 動畫
    }
});