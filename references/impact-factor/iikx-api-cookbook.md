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
| `classid` | 是 | 学科大类（18=跨所有学科的最全查询） | `18` |
| `jcr21` | 否 | JCR 小类（子学科名称，中文） | `工程：生物医学` |
| `orderby` | 否 | 排序字段 | `IF2024`（影响因子降序） |
| `ph` | 是 | 固定值 `1` | `1` |
| `page` | 否 | 页码，0-based | `0`, `1`, `2`... |
| `title` | 否 | 期刊名搜索（部分匹配） | `Biomaterials` |

### 跨大类搜索（推荐）

不指定 `jcr21` 时跨所有学科搜索，获得最全结果：

```bash
# 搜索所有学科中名为 "Biomaterials" 的期刊
curl -s "https://www.iikx.com/api/search/?classid=18&title=Biomaterials&ph=1"
```

### 按小类查询（IF 降序）

```bash
# 查询"工程：生物医学"子类的所有期刊，按 IF 降序
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
        "onlinetime": "NATURE PORTFOLIO",
        "rate": "..."
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

## iikx 可用子学科列表 (jcr21 参数值)

以下为最相关 BME 子类的中文名（直接从 iikx.com data.js 提取）：

### 工程技术大类
```
工程：生物医学
材料科学：生物材料
细胞与组织工程
纳米科技
机器人学
工程：电子与电气
自动化与控制系统
```

### 医学大类
```
医学：研究与实验
细胞生物学
生化与分子生物学
遗传学
免疫学
微生物学
药学
药物化学
肿瘤学
影像医学与核医学
```

### 计算机/AI 大类
```
计算机：人工智能
计算机：跨学科应用
计算机：软件工程
计算机：信息系统
计算机：硬件
计算机：控制论
计算机：理论方法
```

### 其他相关小类
```
生物工程与应用微生物
发育生物学
综合性期刊
生化研究方法
生物物理
生理学
病理学
毒理学
纳米科技
显微镜技术
数学与计算生物学
材料科学：综合
材料科学：复合
材料科学：膜
工程：综合
光谱学
分析化学
物理化学
电化学
高分子科学
能源与燃料
环境科学
生态学
植物科学
食品科技
运筹学与管理科学
遥感
统计学与概率论
绿色可持续发展技术
行为科学
神经科学
精神病学
心理学
老年医学
营养学
运动科学
科学史与科学哲学
人工关能
地质学
地球科学综合
气象与大气科学
海洋学
水资源
自然地理
矿业与矿物加工
矿物学
力学
声学
光学
热力学
物理：综合
物理：应用
物理：凝聚态物理
物理：原子、分子和化学物理
物理：流体与等离子体
物理：数学物理
物理：核物理
物理：粒子与场物理
天文与天体物理
仪器仪表
晶体学
材料科学：表征与测试
材料科学：硅酸盐
材料科学：纸与木材
材料科学：纺织
核科学技术
核医学
成像科学与照相技术
电信学
工程：化工
工程：土木
工程：机械
工程：海洋
工程：环境
工程：地质
工程：宇航
工程：石油
工程：制造
工程：工业
工程：大洋
冶金工程
农业工程
农业综合
农艺学
园艺
奶制品与动物科学
昆虫学
林学
渔业
兽医学
土壤科学
地球化学与地球物理
地质学
古生物学
数学
应用数学
数学跨学科应用
统计学与概率论
逻辑学
社会科学
心理学
运动科学
运输科技
运筹学与管理科学
农业经济与政策
医学：伦理
医学：信息
医学：内科
医学：法
卫生保健与服务
护理
学科教育
```

## Python 批量查询示例

```python
import json, urllib.request, urllib.parse

def query_iikx(jcr21_subcategory=None, title=None, page=0):
    """Query iikx.com API for journal IF data."""
    params = {
        'classid': '18',  # Cross-all-categories
        'orderby': 'IF2024',
        'ph': '1',
        'page': str(page),
    }
    if jcr21_subcategory:
        params['jcr21'] = jcr21_subcategory
    if title:
        params['title'] = title

    url = "https://www.iikx.com/api/search/?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    resp = urllib.request.urlopen(req, timeout=20)
    data = json.loads(resp.read())
    return data['result']

# 分页遍历某小类的全部期刊
all_journals = []
page = 0
while True:
    result = query_iikx(jcr21_subcategory="工程：生物医学", page=page)
    items = result['data']
    if not items:
        break
    all_journals.extend(items)
    print(f"Page {page}: +{len(items)} items")
    page += 1
    if page * int(result['page_size']) >= int(result['total']):
        break

print(f"Total: {len(all_journals)} journals")
for j in sorted(all_journals, key=lambda x: float(x['IF2024']), reverse=True)[:10]:
    print(f"  {j['title'][:50]:50s} IF={j['IF2024']:>8s}  {j['zky2020']}")
```

## 已知限制

1. **顶级期刊缺失**：Nature Methods、PNAS、ACS Nano、Advanced Materials、eLife、Lab on a Chip、Analytical Chemistry 等约 18 本顶级期刊**不在 iikx 数据库**中（iikx 主要收录中文科研者常用的 SCI 期刊）。
2. **分页上限**：每页 15 条，大类别（如"生化与分子生物学"282 刊）需要遍历 ~19 页。
3. **请求间隔**：无公开文档说明速率限制，但实测 0.3s 间隔安全。不要并发超过 5 个请求。
4. **分类交叉**：同一期刊可能出现在多个子类（如 Biomaterials 同时出现在"工程：生物医学"和"材料科学：生物材料"），API 无法去重——需在客户端按 journal ID 去重。
5. **Vue.js 渲染**：前端页面（https://www.iikx.com/sci/list.html）用 Vue.js 渲染，浏览器直接访问看不到表格数据。必须调 `/api/search/` 端点获取 JSON。
6. **中科院分区**：`zky2020` 字段为 2020 版中科院分区，可能与最新版有偏差。
