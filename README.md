Gundam Model Store
基於 Django 的鋼彈模型線上商店，提供產品列表、分類瀏覽、購物車、用戶認證與訂單管理功能，適合模型愛好者購買與管理鋼彈模型。
功能

首頁：展示精選優惠產品，吸引用戶瀏覽。
產品目錄：分頁顯示產品（每頁 9 個產品），包含圖片、價格與描述。
分類瀏覽：支援層次導航與分類橫幅圖片，提升瀏覽體驗。
產品搜尋：支援關鍵字搜尋與分頁結果。
購物車：提供新增、移除、更新商品功能，方便管理購物清單。
用戶認證：支援註冊、登入、登出與個人資料管理（包含頭像上傳）。
訂單管理：支援結帳流程與訂單歷史查詢。
響應式設計：使用 Bootstrap 5.3.7，適配桌面與行動裝置。
本地媒體儲存：產品圖片與用戶頭像儲存於本地檔案系統。

技術棧

後端：Django 5.2，基於 Python 3.10.17。
前端：Bootstrap 5.3.7、純 JavaScript、客製 CSS，無 jQuery 依賴。
資料庫：SQLite（開發環境），支援 PostgreSQL（生產環境）。
儲存：本地檔案系統（開發環境），支援 AWS S3 相容儲存（生產環境）。
認證：Django 內建認證系統，安全可靠。
產品資料：從 products_data.json 匯入產品與分類資料。

系統需求

Python 3.10.17（透過 pyenv 管理）
pip（Python 套件管理器）
Git
pyenv
virtualenvwrapper
可選：Docker（用於容器化部署）
可選：PostgreSQL（生產環境資料庫）

安裝與設定
1. 複製儲存庫
git clone https://github.com/kalpakjian/gundam-store.git
cd gundam-store

2. 建立並啟動虛擬環境
使用 pyenv 和 virtualenvwrapper 設定 Python 3.10.17：
# 確保 pyenv 已安裝並設定 Python 3.10.17
pyenv install 3.10.17
pyenv global 3.10.17

# 安裝 virtualenvwrapper（若尚未安裝）
pip install virtualenvwrapper

# 建立虛擬環境
mkvirtualenv gundam-store

# 啟動虛擬環境
workon gundam-store

3. 安裝依賴
pip install -r requirements.txt

4. 設定環境變數
在專案根目錄建立 .env 檔案，填入以下內容：
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1


注意：請將 SECRET_KEY 設為安全的隨機字串，生產環境切勿使用預設值。

5. 應用資料庫遷移
python manage.py makemigrations
python manage.py migrate

6. 建立超級用戶
python manage.py createsuperuser

7. 收集靜態檔案
python manage.py collectstatic --noinput

8. 啟動開發伺服器
python manage.py runserver

9. 存取應用程式

商店：http://127.0.0.1:8000/
管理後台：http://127.0.0.1:8000/admin/

資料設定
匯入範例資料
從 products_data.json 匯入產品與分類資料：
python manage.py loaddata products_data.json

備份與還原資料
# 建立備份
python manage.py dumpdata > backup.json

# 從備份還原
python manage.py loaddata backup.json

專案結構
gundam-store/
├── gundam_store/          # 主 Django 專案（設定與 URL 配置）
├── accounts/              # 用戶管理應用（認證與個人資料）
├── store/                 # 產品目錄與購物功能
├── static/                # 靜態檔案（CSS、JS、圖片）
├── media/                 # 用戶上傳檔案（產品圖片、頭像）
├── templates/             # HTML 模板
├── requirements.txt       # Python 依賴清單
├── products_data.json     # 產品與分類資料
├── manage.py              # Django 管理腳本
└── README.md              # 本說明文件

開發指南
新增產品

存取管理後台：http://127.0.0.1:8000/admin/
使用超級用戶帳號登入。
導航至 Store > Products，新增產品（包含圖片、價格、描述等）。

客製化

模板：位於 accounts/templates/ 與 store/templates/，可修改 HTML 結構。
靜態檔案：位於 static/（包含 css/、js/、images/ 等）。
模型：定義於 accounts/models.py 與 store/models.py。
視圖：位於 accounts/views.py 與 store/views.py。
產品資料：編輯 products_data.json，並執行 python manage.py loaddata products_data.json 重新匯入。

靜態檔案管理

新增或修改靜態檔案後，執行以下指令更新：python manage.py collectstatic --noinput



生產環境部署
環境變數
在生產環境中，於 .env 檔案設定以下變數：
DEBUG=False
SECRET_KEY=your-production-secret-key
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
DATABASE_URL=postgres://user:password@host:port/database
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
AWS_STORAGE_BUCKET_NAME=your-bucket-name

使用 Docker
# 建置 Docker 映像
docker build -t gundam-store .

# 執行容器
docker run -p 8000:8000 gundam-store

使用 Gunicorn
pip install gunicorn
gunicorn gundam_store.wsgi:application --bind 0.0.0.0:8000


建議：搭配 Nginx 或其他反向代理伺服器，處理靜態檔案與 HTTPS。

貢獻指南

Fork 本儲存庫。
建立功能分支：git checkout -b feature/your-feature-name


提交變更：git commit -m 'Add your feature description'


推送至遠端分支：git push origin feature/your-feature-name


開啟 Pull Request，描述您的變更內容。

致謝
感謝所有貢獻者與鋼彈模型愛好者，您的支持讓本專案更加完善！