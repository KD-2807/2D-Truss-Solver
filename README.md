# Chương trình Phân tích tính toán Hệ Giàn Phẳng 2D

## Giới thiệu

Đây là chương trình hỗ trợ xây dựng và phân tích hệ giàn phẳng 2D bằng phương pháp tĩnh học và phương pháp tách nút. Người dùng có thể tự tạo hệ giàn từ các nút, thanh, vật liệu, tải trọng và gối tựa; tính phản lực liên kết tại các gối và ứng lực dọc trong các thanh; đồng thời xem riêng từng nút hoặc từng thanh để quan sát các lực tác dụng lên đối tượng được chọn.

Chương trình không xét độ võng hay biến dạng của các thanh và nút. Mục tiêu là hỗ trợ việc học tập, trực quan hóa hệ giàn và kiểm tra các đại lượng lực trong mô hình.

Ứng dụng có hai giao diện sử dụng chung phần lõi tính toán:

- **Ứng dụng desktop:** xây dựng bằng PySide6.
- **Ứng dụng web:** xây dựng theo kiến trúc các dịch vụ FastAPI.

Chương trình được phát triển bằng Python và không sử dụng AI trong quá trình tính toán.

## Tính năng chính

### 1. Xây dựng hệ giàn

- Thêm và khai báo các nút (Points) bằng tên và tọa độ $x, y$.
- Thêm các thanh (Members) nối giữa hai nút.
- Khai báo vật liệu (Materials) và các đặc trưng của thanh.
- Thêm tải trọng (Loads) tác dụng tại các nút.
- Đặt gối tựa (Supports) tại các nút.
- Hiển thị hệ trục tọa độ, các nút, thanh, tải trọng và gối tựa.
- Cho phép xây dựng các hệ giàn phẳng khớp nối theo dữ liệu đầu vào.

### 2. Tính toán

- Xác định tọa độ, chiều dài và góc phương của các thanh.
- Thiết lập phương trình cân bằng lực theo hai phương $x$ và $y$ tại từng nút.
- Giải hệ phương trình để xác định phản lực liên kết và ứng lực dọc trong các thanh.
- Phân biệt thanh chịu kéo và thanh chịu nén theo dấu của ứng lực.
- Kiểm tra dữ liệu đầu vào và trạng thái ổn định của hệ.
- Thông báo khi dữ liệu không hợp lệ, hệ mất ổn định hoặc hệ siêu tĩnh chưa thể giải bằng phương pháp hiện tại.

### 3. Xem riêng nút hoặc thanh

- Chọn một nút bất kỳ trên sơ đồ, ví dụ nút B, để chuyển sang chế độ xem riêng nút đó.
- Khi nút được chọn, chương trình hiển thị sơ đồ tách nút với các lực tác dụng, bao gồm tải trọng ngoài, phản lực liên kết nếu có và lực dọc của các thanh nối với nút.
- Hiển thị tên lực, độ lớn, phương, chiều, góc phương và đơn vị.
- Kiểm tra cân bằng lực tại nút được tách.
- Chọn một thanh để xem riêng thanh và các thông tin lực liên quan mà chương trình cung cấp.
- Nhấn **Back** hoặc phím **Esc** để quay lại toàn hệ giàn; sau đó có thể chọn nút hoặc thanh khác.

### 4. Hiển thị kết quả

- Sơ đồ tổng thể của hệ giàn.
- Tên và tọa độ các nút.
- Tên các thanh và các nút đầu–cuối.
- Tải trọng và phản lực được biểu diễn bằng vector.
- Ứng lực dọc trong các thanh, với quy ước dấu kéo/nén.
- Bảng kết quả phản lực và lực trong thanh.
- Trạng thái tính toán và thông báo lỗi.
- Giao diện tiếng Việt và tiếng Anh (VN/EN).

## Cấu trúc thư mục

Cấu trúc thư mục chính của chương trình:

```text
PGK-NNKH/                      # thư mục gốc của dự án
├── main.py                    # điểm khởi chạy: desktop / web / từng dịch vụ
├── requirements.txt           # danh sách thư viện cần cài
├── pytest.ini                 # cấu hình pytest
├── README.md
├── tests/                     # kiểm thử tự động
│   ├── test_core.py
│   ├── test_desktop.py
│   ├── test_presentation.py
│   └── test_services.py
└── trussapp/
    ├── core/
    │   ├── analysis.py
    │   ├── domain.py
    │   ├── errors.py
    │   ├── result_serialization.py
    │   ├── results.py
    │   ├── serialization.py
    │   ├── statics.py
    │   ├── templates.py
    │   ├── validation.py
    │   └── views.py
    ├── desktop/
    │   ├── app.py
    │   ├── canvas.py
    │   ├── controller.py
    │   ├── editors.py
    │   └── main_window.py
    ├── presentation/
    │   ├── i18n.py
    │   ├── panels.py
    │   ├── scene.py
    │   └── selection.py
    └── services/
        ├── clients.py
        ├── gateway.py
        ├── model_service.py
        ├── ports.py
        ├── scene_service.py
        ├── solver_service.py
        └── static/
            ├── app.js
            ├── index.html
            └── style.css
```

Phần `core` đảm nhiệm mô hình dữ liệu, kiểm tra đầu vào và tính toán. Phần `desktop` xây dựng ứng dụng máy tính. Phần `presentation` xử lý nội dung trình bày, ngôn ngữ và lựa chọn đối tượng. Phần `services` cung cấp các dịch vụ và giao diện web. Thư mục `tests` chứa các bộ kiểm thử cho từng phần trên.

Hai giao diện dùng chung phần lõi và các quy ước hiển thị lực nhằm giữ cách biểu diễn nhất quán.

## Yêu cầu hệ thống

### Phần mềm

- **Python 3.10 trở lên** (khuyến nghị 3.11+), kèm `pip`. Mã nguồn dùng cú pháp kiểu dữ liệu `X | None`.
- Hệ điều hành Windows, macOS hoặc Linux. Ứng dụng desktop cần môi trường đồ họa; ứng dụng web chỉ cần trình duyệt.
- Các thư viện khai báo trong `requirements.txt`:

| Thư viện | Phiên bản tối thiểu | Dùng cho |
|---|---|---|
| `numpy` | 1.26 | Giải hệ phương trình cân bằng (lõi tính toán) |
| `PySide6` | 6.6 | Giao diện desktop |
| `fastapi` | 0.110 | Các dịch vụ web |
| `uvicorn[standard]` | 0.29 | Máy chủ chạy các dịch vụ web |
| `httpx` | 0.27 | Các dịch vụ gọi nhau qua HTTP |
| `pytest` | 8 | Chạy kiểm thử |
| `pytest-asyncio` | 0.23 | Kiểm thử các hàm bất đồng bộ |

- Cần kết nối Internet trong lần cài đặt đầu tiên để tải thư viện.

### Phần cứng

Chương trình không yêu cầu phần cứng chuyên dụng. Cấu hình cụ thể phụ thuộc vào môi trường Python và các thư viện được cài đặt (PySide6 chiếm dung lượng đĩa khá lớn khi cài đặt).

## Hướng dẫn cài đặt và chạy chương trình

Tất cả các lệnh dưới đây được chạy **tại thư mục gốc của dự án** (thư mục `PGK-NNKH`, nơi có `main.py` và `requirements.txt`).

### 1. Lấy mã nguồn và kiểm tra Python

Giải nén dự án (hoặc clone về máy), sau đó mở terminal và di chuyển vào thư mục gốc:

```bash
cd PGK-NNKH
python --version
```

Phiên bản Python phải từ 3.10 trở lên. Trên macOS/Linux, nếu lệnh `python` không tồn tại, dùng `python3` thay cho `python` trong toàn bộ hướng dẫn.

### 2. Tạo môi trường ảo (khuyến nghị)

Môi trường ảo giúp tách thư viện của dự án khỏi các dự án Python khác.

**Windows (PowerShell):**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Nếu PowerShell chặn việc chạy script, chạy `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` rồi kích hoạt lại. Với Command Prompt (cmd), dùng `.venv\Scripts\activate.bat`.

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Khi môi trường ảo được kích hoạt, đầu dòng lệnh sẽ hiện `(.venv)`. Mỗi lần mở terminal mới, cần kích hoạt lại môi trường trước khi chạy chương trình.

### 3. Cài đặt thư viện

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Kiểm tra nhanh việc cài đặt:

```bash
python -c "import numpy, fastapi, uvicorn, httpx, PySide6; print('OK')"
```

Nếu in ra `OK` là các thư viện đã sẵn sàng.

> Nếu chỉ dùng ứng dụng web, có thể bỏ qua `PySide6`; nếu chỉ dùng ứng dụng desktop, có thể bỏ qua `fastapi`, `uvicorn` và `httpx`. Tuy nhiên, cài đầy đủ bằng `requirements.txt` là cách đơn giản nhất.

### 4. Chạy ứng dụng desktop

```bash
python main.py desktop
```

Cửa sổ ứng dụng PySide6 sẽ mở ra. Ứng dụng desktop chạy độc lập, không cần khởi động các dịch vụ web.

### 5. Chạy ứng dụng web

```bash
python main.py web
```

Lệnh này khởi động đồng thời 4 tiến trình (dịch vụ) trên máy:

| Dịch vụ | Cổng | Vai trò |
|---|---|---|
| `gateway` | 8000 | Phục vụ giao diện web và cung cấp `/api` công khai |
| `model` | 8001 | Lưu trữ, quản lý và kiểm tra dữ liệu hệ giàn |
| `solver` | 8002 | Giải hệ giàn: phản lực, ứng lực thanh (không lưu trạng thái) |
| `scene` | 8003 | Tạo cảnh hiển thị, bảng kết quả và chế độ xem nút/thanh (gọi `solver` để lấy kết quả) |

Sau khi khởi động, mở địa chỉ sau trên trình duyệt:

```text
http://127.0.0.1:8000
```

Nhấn **Ctrl+C** trong terminal để dừng toàn bộ các dịch vụ. Để kiểm tra trạng thái các dịch vụ, mở `http://127.0.0.1:8000/api/health`.

**Tùy chọn nâng cao:**

- Đổi địa chỉ lắng nghe (ví dụ để máy khác trong mạng LAN truy cập được):

  ```bash
  python main.py web --host 0.0.0.0
  ```

  Có thể đặt thay bằng biến môi trường `HOST`. Chỉ dùng `0.0.0.0` trong mạng tin cậy vì ứng dụng không có cơ chế xác thực.

- Chạy riêng từng dịch vụ (mỗi dịch vụ một terminal, ví dụ khi gỡ lỗi):

  ```bash
  python main.py service solver
  python main.py service model
  python main.py service scene
  python main.py service gateway
  ```

  Tên dịch vụ hợp lệ: `model`, `solver`, `scene`, `gateway`.

- Nếu các dịch vụ chạy ở địa chỉ khác mặc định, khai báo bằng các biến môi trường `MODEL_SERVICE_URL`, `SOLVER_SERVICE_URL`, `SCENE_SERVICE_URL` (mặc định lần lượt là `http://127.0.0.1:8001`, `:8002`, `:8003`).

### 6. Lưu dữ liệu hệ giàn của ứng dụng web

Mặc định, dữ liệu của ứng dụng web được lưu trong bộ nhớ và sẽ mất khi dừng chương trình. Để lưu thành các tệp JSON (mỗi hệ giàn một tệp), đặt biến môi trường `TRUSS_DATA_DIR` **trước khi** chạy; thư mục sẽ được tự tạo nếu chưa có.

**macOS / Linux:**

```bash
TRUSS_DATA_DIR=./data python main.py web
```

**Windows (PowerShell):**

```powershell
$env:TRUSS_DATA_DIR = ".\data"
python main.py web
```

**Windows (cmd):**

```bat
set TRUSS_DATA_DIR=.\data
python main.py web
```

### 7. Chạy kiểm thử

```bash
python -m pytest
```

Cấu hình kiểm thử nằm trong `pytest.ini` (thư mục `tests`, chế độ `asyncio` tự động). Các kiểm thử giao diện desktop tự đặt `QT_QPA_PLATFORM=offscreen` nên có thể chạy trên máy không có màn hình. Nếu cần, có thể đặt biến này thủ công trước khi chạy:

```bash
QT_QPA_PLATFORM=offscreen python -m pytest
```

Chạy riêng từng nhóm kiểm thử:

```bash
python -m pytest tests/test_core.py
python -m pytest tests/test_services.py -v
```

### 8. Sự cố thường gặp khi cài đặt và chạy

| Hiện tượng | Cách xử lý |
|---|---|
| `python: command not found` | Dùng `python3`, hoặc cài Python từ python.org và tick **Add Python to PATH** (Windows). |
| `ModuleNotFoundError: No module named ...` | Chưa kích hoạt môi trường ảo hoặc chưa cài thư viện. Kích hoạt `.venv` rồi chạy lại `python -m pip install -r requirements.txt`. |
| Lỗi cú pháp hoặc lỗi kiểu `str \| None` khi khởi động | Phiên bản Python quá cũ. Dùng Python 3.10 trở lên. |
| `Address already in use` / cổng 8000–8003 đã bị chiếm | Đóng chương trình đang dùng cổng đó (hoặc phiên chạy `main.py web` cũ), rồi chạy lại. |
| `/api/health` báo `unreachable` | Một dịch vụ chưa chạy hoặc `*_SERVICE_URL` sai. Chạy lại bằng `python main.py web` hoặc kiểm tra cổng của từng dịch vụ. |
| Linux: `Could not load the Qt platform plugin "xcb"` | Thiếu thư viện hệ thống cho Qt. Trên Ubuntu/Debian thử `sudo apt install libxcb-cursor0`; trên máy chủ không có màn hình, dùng `QT_QPA_PLATFORM=offscreen` (chỉ phù hợp để kiểm thử, không hiển thị cửa sổ). |
| Trang web không mở được từ máy khác | Chạy với `--host 0.0.0.0` và mở cổng 8000 trên tường lửa. |

## Cách sử dụng

### 1. Khai báo hệ giàn

1. Tạo các nút và nhập tên, tọa độ $x, y$.
2. Tạo các thanh bằng cách chọn nút đầu và nút cuối.
3. Khai báo vật liệu và các thông số tương ứng.
4. Thêm tải trọng tại các nút.
5. Khai báo loại gối tựa và vị trí gối.
6. Kiểm tra sơ đồ trước khi thực hiện tính toán.

### 2. Phân tích hệ giàn

1. Chạy chức năng phân tích hệ giàn.
2. Chương trình kiểm tra dữ liệu đầu vào và điều kiện ổn định.
3. Nếu hệ đủ điều kiện giải, chương trình thiết lập và giải hệ phương trình cân bằng.
4. Xem phản lực tại các gối tựa và ứng lực dọc trong các thanh.
5. Đọc trạng thái tính toán để biết hệ đã giải được hay gặp lỗi.

### 3. Tách nút để xem lực

Ví dụ, khi muốn xem nút B trong toàn hệ:

1. Chọn nút B trên sơ đồ.
2. Chương trình chuyển sang chế độ tách nút B.
3. Sơ đồ riêng thể hiện các lực tác dụng tại nút, gồm tải trọng ngoài, phản lực tại gối (nếu có) và lực dọc của các thanh liên kết với nút B.
4. Xem tên lực, độ lớn, góc phương, chiều và đơn vị; đồng thời kiểm tra điều kiện cân bằng lực tại nút.
5. Nhấn **Back** hoặc **Esc** để trở về sơ đồ toàn hệ.
6. Chọn nút hoặc thanh khác nếu muốn tiếp tục kiểm tra.

Việc tách nút là chế độ hiển thị và phân tích riêng đối tượng; nó không có nghĩa là xóa nút đó khỏi mô hình gốc.

### 4. Xem riêng một thanh

1. Chọn thanh cần kiểm tra.
2. Chương trình chuyển sang chế độ xem riêng thanh.
3. Xem thông tin lực và các dữ liệu liên quan được cung cấp.
4. Quay lại toàn hệ để tiếp tục lựa chọn đối tượng khác.

### 5. Chuyển đổi ngôn ngữ

Sử dụng tùy chọn ngôn ngữ trên giao diện để chuyển giữa tiếng Việt (VN) và tiếng Anh (EN).

## Dữ liệu đầu vào và quy ước

### 1. Points — Nút

| Trường | Ý nghĩa |
|---|---|
| `id` | Mã định danh của nút |
| `name` | Tên nút |
| `x` | Tọa độ theo trục $x$, đơn vị m |
| `y` | Tọa độ theo trục $y$, đơn vị m |

### 2. Members — Thanh

| Trường | Ý nghĩa |
|---|---|
| `id` | Mã định danh của thanh |
| `name` | Tên thanh |
| `start_point` | Mã nút đầu |
| `end_point` | Mã nút cuối |
| `material` | Vật liệu được gán cho thanh |

### 3. Materials — Vật liệu

| Trường | Ý nghĩa | Đơn vị |
|---|---|---|
| `id` | Mã định danh vật liệu | — |
| `name` | Tên vật liệu | — |
| `A` | Diện tích mặt cắt ngang | m² |
| `E` | Mô đun đàn hồi, nhập theo thang $10^9$ Pa | $10^9$ Pa |
| `density` | Khối lượng riêng | kg/m³ |

Các đặc trưng vật liệu được lưu trong mô hình. Phân tích hiện tại tập trung vào cân bằng tĩnh học và không tính độ võng hoặc biến dạng của thanh.

### 4. Loads — Tải trọng

| Trường | Ý nghĩa | Đơn vị |
|---|---|---|
| `id` | Mã định danh tải trọng | — |
| `name` | Tên tải trọng | — |
| `point` | Nút chịu tải | — |
| `Fx` | Thành phần lực theo trục $x$ | N |
| `Fy` | Thành phần lực theo trục $y$ | N |

Trong mô hình giàn khớp nối hiện tại, tải trọng mô-men không được hỗ trợ vì nút khớp không truyền mô-men.

### 5. Supports — Gối tựa

| Loại | Ràng buộc | Phản lực |
|---|---|---|
| `pin` — Gối cố định/khớp | $U_x = U_y = 0$ | $R_x, R_y$ |
| `roller_y` — Gối con lăn theo phương $y$ | $U_y = 0$ | $R_y$ |
| `roller_x` — Gối con lăn theo phương $x$ | $U_x = 0$ | $R_x$ |

Dữ liệu gối tựa gồm `id`, `name`, `point` và `type`. Tên loại liên kết và các thành phần phản lực được xác định theo kiểu gối đã khai báo.

### 6. Hệ tọa độ và dấu

- Sử dụng hệ tọa độ phẳng $O_{xy}$.
- Chiều dương của trục $x$ hướng sang phải.
- Chiều dương của trục $y$ hướng lên trên.
- Ứng lực dọc thanh mang dấu dương khi chịu kéo.
- Ứng lực dọc thanh mang dấu âm khi chịu nén.
- Đơn vị chiều dài là m; lực là N; mô-đun đàn hồi được nhập theo thang $10^9$ Pa; diện tích là m² và khối lượng riêng là kg/m³.

## Output — Kết quả đầu ra

Chương trình cung cấp các thông tin sau:

- Tên và giá trị phản lực tại từng gối tựa.
- Thành phần phản lực theo trục $x$ và $y$, tương ứng với loại gối.
- Ứng lực dọc trong các thanh, với dấu thể hiện kéo hoặc nén.
- Sơ đồ vector lực và thông tin lực khi xem riêng một nút hoặc thanh.
- Tên lực, độ lớn, phương, chiều, góc phương và đơn vị theo chế độ hiển thị.
- Trạng thái tính toán, bao gồm thành công hoặc các dạng lỗi/giới hạn của mô hình.

Các trạng thái chính:

- `solved`: hệ đã được giải.
- `invalid_input`: dữ liệu đầu vào không hợp lệ.
- `unstable_external`: hệ không ổn định về liên kết ngoài.
- `unstable_internal`: hệ mất ổn định bên trong, có thể tạo cơ cấu.
- `indeterminate`: hệ siêu tĩnh theo điều kiện đếm $m + r > 2n$, chưa được giải bằng phương pháp hiện tại.

## Phương pháp tính toán

### 1. Phương pháp tách nút (Method of Joints)

Phương pháp tách nút dựa trên điều kiện cân bằng lực tại mỗi nút của hệ giàn. Với hệ giàn phẳng, tổng lực theo hai phương phải bằng không:

$\sum F_x = 0, \qquad \sum F_y = 0$

Khi tách một nút, các thanh nối vào nút được thay bằng lực dọc thanh tương ứng. Các tải trọng ngoài và phản lực tại gối (nếu nút có gối) cũng được đưa vào sơ đồ lực của nút đó.

### 2. Xác định hình học thanh

Với thanh nối giữa hai nút $i$ và $j$, có tọa độ $(x_i,y_i)$ và $(x_j,y_j)$, chiều dài thanh được xác định bởi:

$L_{ij} = \sqrt{(x_j-x_i)^2 + (y_j-y_i)^2}$

Góc phương của thanh so với trục $x$ được xác định từ chênh lệch tọa độ:

$\theta_{ij} = \operatorname{atan2}(y_j-y_i,\ x_j-x_i)$

Các thành phần phương của thanh được xác định từ $\cos\theta_{ij}$ và $\sin\theta_{ij}$.

### 3. Xác định các ẩn số

Vector ẩn số bao gồm:

- Ứng lực dọc trong các thanh.
- Các thành phần phản lực tại gối tựa.

Các thành phần phản lực phụ thuộc vào loại gối. Gối `pin` có hai thành phần phản lực $R_x, R_y$; gối `roller_y` có $R_y$; gối `roller_x` có $R_x$.

### 4. Thiết lập phương trình cân bằng

Tại mỗi nút, lập hai phương trình cân bằng lực:

$\sum F_x = 0$

$\sum F_y = 0$

Các hệ số của lực dọc thanh trong phương trình được xác định theo góc thanh. Sau khi tổng hợp các phương trình tại các nút, hệ phương trình có dạng:

$Gx = -P$

Trong đó:

- $G$: ma trận hệ số từ hình học thanh, liên kết và phương trình cân bằng.
- $x$: vector ẩn số, gồm ứng lực thanh và phản lực liên kết.
- $P$: vector tải trọng ngoài được sắp xếp theo các thành phần lực tại các nút.

### 5. Giải hệ phương trình

Chương trình giải hệ phương trình cân bằng để tìm các ứng lực dọc thanh và phản lực liên kết. Dấu của ứng lực dọc thanh được dùng để phân biệt:

- $N > 0$: thanh chịu kéo.
- $N < 0$: thanh chịu nén.

Khi xem riêng một nút, chương trình cũng hiển thị kiểm tra cân bằng lực $\sum F_x$ và $\sum F_y$ của nút đó.

### 6. Kiểm tra dữ liệu và trạng thái ổn định

Trước khi hoặc trong quá trình giải, chương trình kiểm tra dữ liệu và phân loại trạng thái hệ. Những trường hợp dữ liệu không hợp lệ, mất ổn định ngoài, mất ổn định trong hoặc siêu tĩnh sẽ được báo trạng thái tương ứng thay vì trả về kết quả như một hệ đã giải thành công.

Điều kiện đếm tham khảo cho hệ giàn phẳng là:

$m + r = 2n$

Trong đó $m$ là số thanh, $r$ là số thành phần phản lực và $n$ là số nút. Điều kiện đếm này không tự nó bảo đảm ổn định hình học; cần xem xét thêm bố trí thanh và liên kết. Trong phạm vi chương trình hiện tại, hệ siêu tĩnh được báo là chưa giải được, do chưa xét biến dạng để giải bài toán siêu tĩnh.

## API của ứng dụng web

Gateway cung cấp các endpoint chính:

| Phương thức | Đường dẫn | Chức năng |
|---|---|---|
| `GET` | `/api/templates` | Lấy danh sách hệ giàn mẫu |
| `POST` | `/api/trusses` | Tạo hệ giàn từ mẫu hoặc dữ liệu hệ giàn |
| `GET` | `/api/trusses/{id}` | Đọc dữ liệu hệ giàn |
| `PUT` | `/api/trusses/{id}` | Cập nhật/lưu dữ liệu hệ giàn |
| `GET` | `/api/trusses/{id}/view?mode=overview&lang=en` | Lấy cảnh tổng thể, bảng kết quả và trạng thái |
| `GET` | `/api/trusses/{id}/view?mode=joint&target=B&lang=en` | Lấy chế độ xem riêng nút B |
| `GET` | `/api/trusses/{id}/view?mode=member&target=AB&lang=en` | Lấy chế độ xem riêng thanh được chọn |
| `GET` | `/api/i18n/{lang}` | Lấy nội dung giao diện theo ngôn ngữ |

Tài liệu tương tác của từng dịch vụ có thể được truy cập tại `/docs` khi dịch vụ tương ứng đang chạy.

## Lưu ý và giới hạn

- Chương trình hiện hỗ trợ hệ giàn phẳng dạng thanh khớp nối.
- Không hỗ trợ gối ngàm.
- Không hỗ trợ tải trọng mô-men tại nút.
- Không tính độ võng hoặc biến dạng của thanh và nút.
- Hệ siêu tĩnh được nhận diện và báo trạng thái, nhưng chưa được giải.
- Kết quả phụ thuộc vào tính đúng đắn của tọa độ, kết nối thanh, tải trọng và điều kiện gối tựa do người dùng nhập.
- Cần kiểm tra đơn vị và chiều dấu của tải trọng trước khi phân tích.

## Xử lý lỗi thường gặp

### 1. Dữ liệu đầu vào không hợp lệ

Kiểm tra mã nút, tọa độ, kết nối đầu–cuối của thanh, vật liệu, tải trọng và loại gối tựa. Đảm bảo các tham chiếu trong dữ liệu trỏ đến đối tượng tồn tại.

### 2. Hệ mất ổn định ngoài

Kiểm tra số lượng, loại và cách bố trí gối tựa. Các ràng buộc phải ngăn được chuyển động vật rắn của toàn hệ.

### 3. Hệ mất ổn định trong

Kiểm tra cách bố trí các thanh và liên kết giữa các nút; hệ có thể tạo thành cơ cấu nếu cấu hình thanh không đủ ổn định.

### 4. Hệ siêu tĩnh

Chương trình hiện báo trạng thái `indeterminate` và không giải hệ siêu tĩnh bằng phương pháp hiện tại. Mô hình cần phương pháp xét biến dạng nếu muốn giải loại hệ này.

## Tác giả

- Phan Gia Khang
- Nguyen Ngoc Khanh Hoang

## Giấy phép

Dự án được phát triển phục vụ mục đích học tập và nghiên cứu.

## Ví dụ minh họa quy trình phân tích

Giả sử người dùng tạo một hệ giàn phẳng gồm các nút, thanh, tải trọng và gối tựa:

1. Nhập tọa độ các nút và kết nối các thanh.
2. Khai báo vật liệu, tải trọng và gối tựa.
3. Chạy phân tích để nhận phản lực tại các gối và ứng lực dọc trong các thanh.
4. Chọn một nút, ví dụ B, để mở sơ đồ tách nút.
5. Quan sát các vector lực tác dụng lên nút B và kiểm tra cân bằng lực.
6. Nhấn **Back** hoặc **Esc** để trở về toàn hệ và tiếp tục chọn đối tượng khác.

## Tùy chỉnh
1. Ngôn ngữ: i18n.py
2. Ví dụ: templates.py

README nguồn không cung cấp một bộ tọa độ, tải trọng và hình vẽ số cụ thể để xác lập một ví dụ tính toán có kết quả số; vì vậy phần này mô tả quy trình sử dụng thay vì tự đặt số liệu giả định.
=======
# 2D-Truss-Solver
HCMUT Projects
