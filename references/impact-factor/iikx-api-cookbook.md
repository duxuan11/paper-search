# Iikx.com SCI Impact Factor API Cookbook

> 爱科学 (iikx.com) 是一个免费的 SCI 期刊影响因子查询平台，提供后台 JSON API。
> 发现日期：2026-06-16 | 数据字段：IF2024 (2024 JCR Impact Factor)

## API Base URL

```
https://www.iikx.com/api/search/
```

### 核心参数

| 参数 | 必填 | 说明 | 示例值 |
|------|------|------|--------|
| `classid` | 是 | 学科大类（18=跨所有 14 个学科的最全查询） | `18` |
| `jcr21` | 否 | JCR 小类（子学科名称，中文） | `工程：生物医学` |
| `orderby` | 否 | 排序字段 | `IF2024`（影响因子降序） |
| `ph` | 是 | 固定值 `1` | `1` |
| `page` | 否 | 页码，0-based | `0`, `1`, `2`... |
| `title` | 否 | 期刊名搜索（部分匹配） | `Biomaterials` |

### classid=18 覆盖的学科大类

| ID | 学科 |
|:--:|------|
| 125 | 医学 |
| 124 | 生物 |
| 126 | 农林科学 |
| 127 | 环境科学与生态学 |
| 128 | 化学 |
| 129 | 工程技术 |
| 130 | 数学 |
| 131 | 物理 |
| 132 | 地学 |
| 133 | 地学天文 |
| 134 | 社会科学 |
| 135 | 管理科学 |
| 123 | 综合性期刊 |
| 136 | 其他 |

### 跨大类搜索（推荐）

```bash
curl -s "https://www.iikx.com/api/search/?classid=18&title=Biomaterials&ph=1"
```

### 按小类查询（IF 降序）

```bash
curl -s "https://www.iikx.com/api/search/?classid=18&jcr21=%E5%B7%A5%E7%A8%8B%EF%BC%9A%E7%94%9F%E7%89%A9%E5%8C%BB%E5%AD%A6&orderby=IF2024&ph=1&page=0"
```

## Response 结构

```json
{
  "code": 200,
  "result": {
    "total": 58,
    "current_page": 0,
    "page_size": 15,
    "data": [
      {
        "id": "19753",
        "title": "Nature Biomedical Engineering",
        "smalltitle": "NAT BIOMED ENG",
        "IF2024": "26.6",
        "IF2023": "28.1",
        "zky2020": "Q1",
        "category": "ENGINEERING, BIOMEDICAL - SCIE",
        "jcr21": "工程：生物医学",
        "issn": "2157-846X",
        "eissn": "2157-846X",
        "onlinetime": "NATURE PORTFOLIO"
      }
    ]
  }
}
```

### 关键字段

| 字段 | 含义 |
|------|------|
| `title` | 期刊全名 |
| `smalltitle` | 期刊缩写 |
| `IF2024` | 2024 年影响因子（最新） |
| `IF2023` | 2023 年影响因子 |
| `zky2020` | 中科院分区 (Q1/Q2/Q3/Q4) |
| `category` | SCIE 学科分类 |
| `jcr21` | JCR 小类（中文） |
| `issn` / `eissn` | ISSN 号 |
| `onlinetime` | 出版商 |

## 批量查询工作流（2026-06-16 实测模式）

本会话中验证的完整流程（从 iikx.com 获取 1,405 篇不重复期刊）：

### 步骤 1：选择子类

BME 核心推荐：

```
工程：生物医学       → 58 刊
细胞与组织工程       → 23 刊
材料科学：生物材料   → 10 刊
生物工程与应用微生物 → 124 刊
生化与分子生物学     → 282 刊（最大）
细胞生物学           → 118 刊
免疫学               → 113 刊
遗传学               → 96 刊
计算机：人工智能     → 131 刊
计算机：跨学科应用   → 72 刊
医学：研究与实验     → 78 刊
影像医学与核医学     → 64 刊
综合性期刊           → 67 刊
发育生物学           → 26 刊
纳米科技             → 6 刊
机器人学             → 12 刊
```

### 步骤 2：去重

同一期刊可能出现在多个子类。**必须在客户端按 `id` 字段去重**。

### 步骤 3：Python 分页遍历

```python
import json, urllib.request, urllib.parse

def query_iikx(jcr21_subcategory=None, title=None, page=0):
    params = {'classid': '18', 'orderby': 'IF2024', 'ph': '1', 'page': str(page)}
    if jcr21_subcategory: params['jcr21'] = jcr21_subcategory
    if title: params['title'] = title
    url = "https://www.iikx.com/api/search/?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    resp = urllib.request.urlopen(req, timeout=20)
    return json.loads(resp.read())['result']

# 分页 + 去重
all_journals, seen_ids = {}, set()
for cat in ["工程：生物医学", "细胞与组织工程", "材料科学：生物材料",
            "生物工程与应用微生物", "生化与分子生物学", "细胞生物学",
            "免疫学", "遗传学", "计算机：人工智能", "计算机：跨学科应用",
            "医学：研究与实验", "影像医学与核医学", "综合性期刊",
            "发育生物学", "纳米科技", "机器人学"]:
    page = 0
    while True:
        result = query_iikx(jcr21_subcategory=cat, page=page)
        items = result['data']
        if not items: break
        for item in items:
            if item['id'] not in seen_ids:
                seen_ids.add(item['id'])
                all_journals[item['id']] = item
        page += 1

# 按 IF 降序
sorted_j = sorted(all_journals.values(),
    key=lambda x: float(x['IF2024']) if x['IF2024'].replace('.','',1).isdigit() else -1,
    reverse=True)
print(f"Total unique: {len(sorted_j)}")
for j in sorted_j[:10]:
    print(f"{j['title'][:50]:50s} IF={j['IF2024']:>8s}  {j['zky2020']}")
```

## iikx 可用子学科列表 (jcr21 参数值)

### 工程技术
工程：生物医学、材料科学：生物材料、细胞与组织工程、纳米科技、机器人学、工程：电子与电气、自动化与控制系统、工程：化工、工程：土木、工程：机械、工程：环境、工程：综合、工程：制造、工程：工业

### 医学
医学：研究与实验、细胞生物学、生化与分子生物学、遗传学、免疫学、微生物学、药学、药物化学、肿瘤学、影像医学与核医学、心脏和心血管系统、胃肠肝病学、血液学、神经科学、精神病学、眼科学、耳鼻喉科学、皮肤病学、骨科、妇产科学、儿科、外科

### 计算机/AI
计算机：人工智能、计算机：跨学科应用、计算机：软件工程、计算机：信息系统、计算机：硬件、计算机：控制论、计算机：理论方法

### 生物/生化
生物工程与应用微生物、发育生物学、综合性期刊、生化研究方法、生物物理、生理学、病理学、毒理学、显微镜技术、数学与计算生物学、生态学、进化生物学

### 材料/化学
材料科学：综合、材料科学：复合、材料科学：膜、材料科学：表征与测试、材料科学：硅酸盐、分析化学、物理化学、电化学、高分子科学、有机化学、无机化学与核化学

### 物理/数学
物理：应用、物理：凝聚态物理、物理：综合、数学、应用数学、统计学与概率论、光学、力学、热力学、声学

### 其他
能源与燃料、环境科学、地球科学综合、遥感、食品科技、运筹学与管理科学、绿色可持续发展技术、行为科学、老年医学、营养学、运动科学

## 已知限制

1. **顶级期刊缺失**：约 18 本顶级期刊不在 iikx 数据库中，包括 Nature Methods, PNAS, ACS Nano, Advanced Materials, eLife, Lab on a Chip, Analytical Chemistry, Advanced Science, Advanced Functional Materials, Nano Letters, Nature Protocols, Communications Biology, MedComm, Military Medical Research, Materials Today, Small, Angiogenesis 等。
2. **分页上限**：每页 15 条，大类别需遍历 19 页。page 递增到空数组终止。
3. **请求间隔**：建议 0.3s+ 间隔。不要并发超过 5 个请求。
4. **分类交叉去重**：必须在客户端按 `id` 字段去重。
5. **Vue.js 渲染**：前端页面用 Vue.js 渲染，必须调 `/api/search/` 端点获取 JSON。
6. **中科院分区**：`zky2020` 字段为 2020 版中科院分区，可能与最新版有偏差。

## 2026-06-16 会话实测数据

| 指标 | 值 |
|------|-----|
| 查询子类数 | 20 |
| 获取不重复期刊 | 1,405 |
| 整理后入表 | 372（12 大类） |
| 含 IF 数据 | 371 (99.7%) |
| 总耗时（全量） | ~160s |
| 标 [需核实] 条目 | 18 |
