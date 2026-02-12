# PyCaret MCP Server

MCP Server สำหรับ PyCaret ที่ให้ Claude Desktop สามารถเข้าถึงและสอบถามข้อมูลเกี่ยวกับชุดข้อมูลตัวอย่างใน PyCaret ได้

## คุณสมบัติ (Features)

- **รายชื่อชุดข้อมูล**: ดูรายชื่อชุดข้อมูลตัวอย่างทั้งหมดที่มีใน PyCaret
- **โหลดข้อมูล**: โหลดชุดข้อมูลเพื่อดูรายละเอียด
- **ข้อมูลรายละเอียด**: ดูข้อมูลสถิติ, ประเภทข้อมูล, ค่าที่หายไป
- **ข้อมูลคอลัมน์**: สอบถามข้อมูลของคอลัมน์เฉพาะ

## การติดตั้ง (Installation)

### 1. ติดตั้ง Dependencies

```powershell
cd "d:/งานทั้งหมด/งานปี 3 เทอม 1/dstoolbox/Ml-Pipeline/ML-Pipeline/pycaret-mcp-server"
uv sync
```

หรือใช้ pip:

```powershell
pip install -e .
```

### 2. ตั้งค่า Claude Desktop

เพิ่มการตั้งค่าใน `claude_desktop_config.json`:

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "pycaret": {
      "command": "uv",
      "args": [
        "--directory",
        "d:/งานทั้งหมด/งานปี 3 เทอม 1/dstoolbox/Ml-Pipeline/ML-Pipeline/pycaret-mcp-server",
        "run",
        "pycaret-mcp-server"
      ]
    }
  }
}
```

หากใช้ Python environment แทน uv:

```json
{
  "mcpServers": {
    "pycaret": {
      "command": "python",
      "args": [
        "-m",
        "pycaret_mcp.server"
      ],
      "env": {
        "PYTHONPATH": "d:/งานทั้งหมด/งานปี 3 เทอม 1/dstoolbox/Ml-Pipeline/ML-Pipeline/pycaret-mcp-server/src"
      }
    }
  }
}
```

### 3. รีสตาร์ท Claude Desktop

ปิดและเปิด Claude Desktop อีกครั้งเพื่อให้โหลด MCP server

## การใช้งาน (Usage)

หลังจากติดตั้งเรียบร้อยแล้ว คุณสามารถถามคำถามกับ Claude ได้เลย:

### ตัวอย่างคำถามภาษาไทย:

- "ขอดูรายชื่อชุดข้อมูลตัวอย่างใน PyCaret หน่อย"
- "โหลดชุดข้อมูล diabetes ให้หน่อย"
- "ข้อมูล diabetes มีกี่แถว กี่คอลัมน์?"
- "อธิบายชุดข้อมูล diabetes"
- "ดูข้อมูลคอลัมน์ Age ในชุดข้อมูลปัจจุบัน"

### Example Questions (English):

- "Show me available PyCaret datasets"
- "Load the diabetes dataset"
- "What is the shape of the current dataset?"
- "Show detailed information about the dataset"
- "Get information about the Age column"

## เครื่องมือที่มี (Available Tools)

1. **list_datasets**: แสดงรายชื่อชุดข้อมูลทั้งหมด
2. **load_dataset**: โหลดชุดข้อมูลตามชื่อ
3. **get_dataset_info**: ดูข้อมูลรายละเอียดของชุดข้อมูลปัจจุบัน
4. **get_dataset_shape**: ดูขนาด (rows, columns) ของชุดข้อมูล
5. **get_column_info**: ดูข้อมูลของคอลัมน์เฉพาะ

## ชุดข้อมูลที่รองรับ (Supported Datasets)

- diabetes
- iris
- credit
- juice
- bank
- blood
- cancer
- heart
- hepatitis
- income
- insurance
- parkinsons
- pokemon
- satellite
- telescope
- wine

## การทดสอบ (Testing)

ทดสอบ server โดยตรง:

```powershell
cd "d:/งานทั้งหมด/งานปี 3 เทอม 1/dstoolbox/Ml-Pipeline/ML-Pipeline/pycaret-mcp-server"
uv run pycaret-mcp-server
```

Server จะรอรับ input จาก stdio (MCP protocol)

## โครงสร้างโปรเจกต์ (Project Structure)

```
pycaret-mcp-server/
├── src/
│   └── pycaret_mcp/
│       ├── __init__.py
│       └── server.py       # MCP server implementation
├── pyproject.toml          # Project configuration
└── README.md              # This file
```

## License

MIT
