"""
命理学结构化决策分析 — AI Studio 单文件版
从八字五行中提取系统思维，去掉玄学，只留结构。
"""
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

# ============================================================
# 五要素
# ============================================================
class Element(Enum):
    WOOD  = "木"
    FIRE  = "火"
    EARTH = "土"
    METAL = "金"
    WATER = "水"

    @property
    def label(self):
        return {"木":"生长力(创造/扩张/突破)","火":"表现力(影响/展示/沟通)",
                "土":"承载力(稳定/基础/信任)","金":"收敛力(决断/规则/取舍)",
                "水":"流动力(信息/人脉/适应)"}[self.value]

GENERATES = {Element.WOOD:Element.FIRE,Element.FIRE:Element.EARTH,
             Element.EARTH:Element.METAL,Element.METAL:Element.WATER,
             Element.WATER:Element.WOOD}
CONTROLS = {Element.WOOD:Element.EARTH,Element.EARTH:Element.WATER,
            Element.WATER:Element.FIRE,Element.FIRE:Element.METAL,
            Element.METAL:Element.WOOD}

class Role(Enum):
    SELF="比肩";PEER="劫财";RESOURCE="正印";MENTOR="偏印"
    OUTPUT="食神";TALENT="伤官";WEALTH="正财";GAMBLE="偏财"
    AUTHORITY="正官";PRESSURE="七杀"

class Pillar(Enum):
    YEAR="年柱";MONTH="月柱";DAY="日柱";HOUR="时柱"

@dataclass
class Stakeholder:
    name:str;role:Role;element:Element;strength:int;description:str=""

@dataclass
class Phase:
    name:str;element:Element;duration:str;quality:str;description:str;key_action:str=""

@dataclass
class Dimension:
    pillar:Pillar;element:Element;strength:int;description:str

@dataclass
class Situation:
    question:str;context:str="";dimensions:list=field(default_factory=list)
    stakeholders:list=field(default_factory=list);phases:list=field(default_factory=list)

ROLE_MAP = {"比肩":Role.SELF,"劫财":Role.PEER,"正印":Role.RESOURCE,"偏印":Role.MENTOR,
            "食神":Role.OUTPUT,"伤官":Role.TALENT,"正财":Role.WEALTH,"偏财":Role.GAMBLE,
            "正官":Role.AUTHORITY,"七杀":Role.PRESSURE}
ELEM_MAP = {"木":Element.WOOD,"火":Element.FIRE,"土":Element.EARTH,"金":Element.METAL,"水":Element.WATER}

class MetaphorAnalyzer:
    def __init__(self, s): self.sit = s

    def analyze_balance(self):
        counts = {e:0 for e in Element}
        for d in self.sit.dimensions: counts[d.element] += d.strength
        for s in self.sit.stakeholders: counts[s.element] += s.strength * 0.5
        total = sum(counts.values()) or 1
        ratios = {e.value:round(v/total*100,1) for e,v in counts.items()}
        avg = total/5
        excess = {e.value:round(v-avg,1) for e,v in counts.items() if v>avg*1.5}
        deficient = {e.value:round(avg-v,1) for e,v in counts.items() if avg>0 and v/avg<0.3}
        return {"分布":ratios,"过旺":excess,"不足":deficient}

    def analyze_relations(self):
        rels = []
        factors = [(d.pillar.value,d.element,d.strength) for d in self.sit.dimensions]
        factors += [(f"[{s.role.value}]{s.name}",s.element,s.strength) for s in self.sit.stakeholders]
        for i,(na,ea,sa) in enumerate(factors):
            for j,(nb,eb,sb) in enumerate(factors):
                if i>=j: continue
                r=None
                if GENERATES.get(ea)==eb: r=("生",sa*0.8)
                elif GENERATES.get(eb)==ea: r=("生",sb*0.8)
                elif CONTROLS.get(ea)==eb: r=("克",sa*0.6)
                elif CONTROLS.get(eb)==ea: r=("克",sb*0.6)
                if r: rels.append({"A":na,"B":nb,"关系":r[0],"力度":round(r[1],1),"说明":f"{na}({ea.value}) {r[0]} {nb}({eb.value})"})
        rels.sort(key=lambda x:x["力度"],reverse=True)
        return rels

    def analyze_roles(self):
        rm = {}
        for s in self.sit.stakeholders:
            rm[s.role.value] = {"名称":s.name,"力量":s.element.value,"强度":s.strength,"说明":s.description}
        has_sup = any(s.role in (Role.RESOURCE,Role.MENTOR) for s in self.sit.stakeholders)
        has_pre = any(s.role in (Role.AUTHORITY,Role.PRESSURE) for s in self.sit.stakeholders)
        if has_sup and not has_pre: pat,adv="印格（有支持，压力小）","利用支持力量，加速推进"
        elif has_pre and not has_sup: pat,adv="杀格（压力大，缺支持）","先化解压力，再谈发展"
        elif has_sup and has_pre: pat,adv="官印相生（有压力也有支持）","借力支持，转化压力"
        else: pat,adv="中性格局","需要更多信息"
        return {"角色分布":rm,"格局判断":pat,"策略建议":adv}

    def analyze_phases(self):
        if not self.sit.phases: return {"阶段":[],"整体趋势":"未设定"}
        pa = [{"阶段":p.name,"时间":p.duration,"主导":f"{p.element.value}({p.element.label})",
               "质量":p.quality,"说明":p.description,"行动":p.key_action} for p in self.sit.phases]
        qs = [p.quality for p in self.sit.phases]
        if qs[-1]=="有利" and qs[0]!="有利": t="先抑后扬（V型反转）"
        elif qs[0]=="有利" and qs[-1]!="有利": t="先扬后抑（冲高回落）"
        elif all(q=="有利" for q in qs): t="持续向好"
        elif all(q=="不利" for q in qs): t="持续承压"
        else: t="起伏交替"
        return {"阶段":pa,"整体趋势":t}

    def full_report(self):
        b=self.analyze_balance(); r=self.analyze_relations()
        ro=self.analyze_roles(); p=self.analyze_phases()
        lines=["="*50,f"  问题：{self.sit.question}","="*50,""]
        lines.append("【一、五要素平衡】")
        for e,pct in b["分布"].items():
            bar="█"*int(pct/5)+"░"*(20-int(pct/5))
            lines.append(f"  {e} {bar} {pct}%")
        if b["过旺"]: lines.append(f"  ⚠ 过旺：{', '.join(b['过旺'].keys())}")
        if b["不足"]: lines.append(f"  ⚠ 不足：{', '.join(b['不足'].keys())}")
        lines.append("")
        lines.append("【二、关系网络】")
        for x in r[:8]:
            icon="➕" if x["关系"]=="生" else "⚔️"
            lines.append(f"  {icon} {x['说明']}  [力度:{x['力度']}]")
        lines.append("")
        lines.append("【三、角色格局】")
        for role,info in ro["角色分布"].items():
            lines.append(f"  [{role}] {info['名称']} — {info['力量']} 强度:{info['强度']}")
        lines.append(f"  格局：{ro['格局判断']}")
        lines.append(f"  策略：{ro['策略建议']}")
        if p["阶段"]:
            lines.append("")
            lines.append("【四、阶段推演】")
            for x in p["阶段"]:
                icon="🟢" if x["质量"]=="有利" else ("🔴" if x["质量"]=="不利" else "🟡")
                lines.append(f"  {icon} {x['阶段']}({x['时间']})：{x['说明']}")
                if x["行动"]: lines.append(f"     → {x['行动']}")
            lines.append(f"  趋势：{p['整体趋势']}")
        lines.append("")
        lines.append("【综合判断】")
        lines.append(f"  格局：{ro['格局判断']}")
        lines.append(f"  策略：{ro['策略建议']}")
        if r: lines.append(f"  核心力量：{r[0]['说明']}")
        if p.get("阶段"): lines.append(f"  时间趋势：{p['整体趋势']}")
        lines.append("="*50)
        return "\n".join(lines), {"balance":b,"relations":r,"roles":ro,"phases":p}


def build_from_dict(data: dict) -> Situation:
    dims = [
        Dimension(Pillar.YEAR, ELEM_MAP[data["environment"]["element"]], data["environment"]["strength"], data["environment"]["description"]),
        Dimension(Pillar.MONTH, ELEM_MAP[data["situation"]["element"]], data["situation"]["strength"], data["situation"]["description"]),
        Dimension(Pillar.DAY, ELEM_MAP[data["self_state"]["element"]], data["self_state"]["strength"], data["self_state"]["description"]),
        Dimension(Pillar.HOUR, ELEM_MAP[data["goal"]["element"]], data["goal"]["strength"], data["goal"]["description"]),
    ]
    shs = [Stakeholder(s["name"], ROLE_MAP[s["role"]], ELEM_MAP[s["element"]], s["strength"], s["description"]) for s in data.get("stakeholders",[])]
    phs = [Phase(p["name"], ELEM_MAP[p["element"]], p["duration"], p["quality"], p["description"], p.get("key_action","")) for p in data.get("phases",[])]
    return Situation(data["question"], data.get("context",""), dims, shs, phs)


# ============================================================
# Web App (FastAPI)
# ============================================================
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI(title="命理学结构化决策分析")

class AnalysisRequest(BaseModel):
    question:str;context:str=""
    environment:dict;situation:dict;self_state:dict;goal:dict
    stakeholders:list=[];phases:list=[]

@app.post("/api/analyze")
async def analyze(req: AnalysisRequest):
    try:
        sit = build_from_dict(req.dict())
        az = MetaphorAnalyzer(sit)
        report, data = az.full_report()
        return {"success":True,"report":report,**data}
    except Exception as e:
        return {"success":False,"error":str(e)}

@app.get("/api/demo")
async def demo():
    req = AnalysisRequest(
        question="要不要从现在的公司跳槽去创业公司？",
        context="在大厂工作3年，薪资稳定但晋升慢。创业公司给了offer，薪资+30%但有风险。",
        environment={"element":"水","strength":7,"description":"经济环境不确定，市场流动性大"},
        situation={"element":"金","strength":8,"description":"大厂稳定但天花板明显"},
        self_state={"element":"木","strength":7,"description":"有创造力想做事，但被环境压制"},
        goal={"element":"火","strength":6,"description":"想要更大的影响力和成长空间"},
        stakeholders=[
            {"name":"大厂体系","role":"正官","element":"金","strength":8,"description":"制度约束、晋升缓慢"},
            {"name":"创业公司CEO","role":"正印","element":"木","strength":7,"description":"给你机会和空间"},
            {"name":"同事小王","role":"劫财","element":"木","strength":5,"description":"也在考虑跳槽"},
            {"name":"家人","role":"偏印","element":"土","strength":6,"description":"建议求稳"},
            {"name":"市场不确定性","role":"七杀","element":"水","strength":7,"description":"创业失败概率"},
        ],
        phases=[
            {"name":"现状期","element":"金","duration":"当前","quality":"中性","description":"稳定但无突破","key_action":"盘点核心能力"},
            {"name":"决策期","element":"木","duration":"1-2个月","quality":"有利","description":"信息充分选择清晰","key_action":"深入聊一次"},
            {"name":"过渡期","element":"火","duration":"3-6个月","quality":"不利","description":"转换成本高","key_action":"提前积累"},
            {"name":"稳定期","element":"土","duration":"半年后","quality":"有利","description":"新环境稳定","key_action":"建立不可替代性"},
        ],
    )
    return await analyze(req)

HTML = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>命理学结构化决策分析</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
:root{--bg:#0a0a0f;--card:#12121a;--border:#1e1e2e;--text:#e0e0e8;--muted:#8888a0;--accent:#6c5ce7;--accent2:#00cec9;--good:#2ecc71;--bad:#e74c3c;--mid:#f39c12}
body{background:var(--bg);color:var(--text);font-family:'SF Mono','Fira Code','Consolas',monospace;min-height:100vh;padding:20px}
.container{max-width:960px;margin:0 auto}
.header{text-align:center;padding:40px 0 30px;border-bottom:1px solid var(--border);margin-bottom:30px}
.header h1{font-size:28px;background:linear-gradient(135deg,var(--accent),var(--accent2));-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.header p{color:var(--muted);font-size:13px;margin-top:8px}
.section{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:24px;margin-bottom:20px}
.section-title{font-size:16px;font-weight:700;margin-bottom:16px;display:flex;align-items:center;gap:8px}
.dot{width:8px;height:8px;border-radius:50%;display:inline-block;background:var(--accent)}
label{display:block;font-size:12px;color:var(--muted);margin:12px 0 4px}
label:first-child{margin-top:0}
input,textarea,select{width:100%;background:var(--bg);border:1px solid var(--border);border-radius:8px;padding:10px 12px;color:var(--text);font-family:inherit;font-size:14px;outline:none}
input:focus,textarea:focus,select:focus{border-color:var(--accent)}
textarea{resize:vertical;min-height:60px}
.row{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.row-3{display:grid;grid-template-columns:1fr 80px 1fr;gap:12px}
input[type=range]{-webkit-appearance:none;height:6px;border-radius:3px;background:var(--border);border:none;margin-top:16px}
input[type=range]::-webkit-slider-thumb{-webkit-appearance:none;width:18px;height:18px;border-radius:50%;background:var(--accent);cursor:pointer}
.range-val{text-align:center;font-size:20px;font-weight:700;color:var(--accent2);margin-top:4px}
.sh-item,.ph-item{background:var(--bg);border:1px solid var(--border);border-radius:8px;padding:14px;margin-bottom:10px;position:relative}
.rm{position:absolute;top:8px;right:8px;background:none;border:none;color:var(--muted);cursor:pointer;font-size:16px}
.rm:hover{color:var(--bad)}
.btn{display:inline-flex;align-items:center;gap:6px;padding:10px 18px;border:1px solid var(--border);border-radius:8px;background:var(--card);color:var(--text);font-family:inherit;font-size:13px;cursor:pointer;transition:all .2s}
.btn:hover{border-color:var(--accent)}
.btn-primary{background:linear-gradient(135deg,var(--accent),#8b5cf6);border:none;color:#fff;font-size:15px;padding:14px 32px;font-weight:700}
.btn-primary:hover{transform:translateY(-1px);box-shadow:0 4px 20px rgba(108,92,231,.3)}
.btn-primary:disabled{opacity:.5;cursor:wait;transform:none}
.btn-demo{background:transparent;border:1px dashed var(--accent2);color:var(--accent2)}
.btn-row{display:flex;gap:12px;justify-content:center;margin:30px 0;flex-wrap:wrap}
#result{display:none}#result.show{display:block}
.rc{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:24px;margin-bottom:20px}
.rc h3{font-size:15px;margin-bottom:16px;color:var(--accent2)}
.bb{display:flex;align-items:center;gap:10px;margin-bottom:8px}
.bb .bl{width:30px;font-size:14px;font-weight:700}
.bb .bg{flex:1;height:24px;background:var(--bg);border-radius:4px;overflow:hidden}
.bb .bf{height:100%;border-radius:4px;transition:width .6s;display:flex;align-items:center;padding-left:8px;font-size:11px;font-weight:700;color:#fff}
.bf-w{background:linear-gradient(90deg,#27ae60,#2ecc71)}.bf-f{background:linear-gradient(90deg,#c0392b,#e74c3c)}
.bf-e{background:linear-gradient(90deg,#e67e22,#f39c12)}.bf-m{background:linear-gradient(90deg,#95a5a6,#bdc3c7);color:#333!important}
.bf-a{background:linear-gradient(90deg,#2980b9,#3498db)}
.ri{display:flex;align-items:center;gap:8px;padding:8px 0;border-bottom:1px solid var(--border);font-size:13px}
.ri:last-child{border-bottom:none}.ri .rp{margin-left:auto;background:var(--bg);padding:2px 8px;border-radius:4px;font-size:11px;color:var(--muted)}
.roli{display:flex;align-items:center;gap:12px;padding:10px 0;border-bottom:1px solid var(--border);flex-wrap:wrap}
.roli:last-child{border-bottom:none}
.rb{background:var(--accent);color:#fff;padding:2px 10px;border-radius:4px;font-size:12px;font-weight:700;white-space:nowrap}
.rs{margin-left:auto;display:flex;gap:2px}.rs .p{width:8px;height:8px;border-radius:50%;background:var(--border)}.rs .p.a{background:var(--accent2)}
.tl{position:relative;padding-left:24px}.tl::before{content:'';position:absolute;left:8px;top:0;bottom:0;width:2px;background:var(--border)}
.ti{position:relative;padding-bottom:20px}.ti::before{content:'';position:absolute;left:-20px;top:6px;width:12px;height:12px;border-radius:50%;border:2px solid var(--border);background:var(--bg)}
.ti.g::before{border-color:var(--good);background:var(--good)}.ti.b::before{border-color:var(--bad);background:var(--bad)}.ti.m::before{border-color:var(--mid);background:var(--mid)}
.ti .tt{font-weight:700;font-size:14px}.ti .td{font-size:13px;color:var(--muted);margin-top:4px}.ti .ta{font-size:12px;color:var(--accent2);margin-top:4px}
.syn{background:linear-gradient(135deg,rgba(108,92,231,.1),rgba(0,206,201,.1));border:1px solid var(--accent);border-radius:12px;padding:24px;font-size:14px;line-height:1.8}
.syn p{margin-bottom:8px}syn strong{color:var(--accent2)}
.raw{background:var(--bg);border:1px solid var(--border);border-radius:8px;padding:16px;font-size:12px;white-space:pre-wrap;line-height:1.6;color:var(--muted);max-height:400px;overflow-y:auto}
.tip{background:rgba(108,92,231,.08);border-left:3px solid var(--accent);padding:12px 16px;font-size:12px;color:var(--muted);border-radius:0 8px 8px 0;margin-bottom:16px}
.ld{text-align:center;padding:40px;color:var(--muted)}.sp{display:inline-block;width:24px;height:24px;border:3px solid var(--border);border-top-color:var(--accent);border-radius:50%;animation:spin .8s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
</style>
</head>
<body>
<div class="container">
<div class="header">
<h1>☯ 命理学结构化决策分析</h1>
<p>从八字五行中提取系统思维 · 去掉玄学 · 只留结构</p>
</div>
<div class="section">
<div class="section-title"><span class="dot"></span>你要分析的问题</div>
<label>具体问题</label><input type="text" id="q" placeholder="例：要不要跳槽？这个项目该不该继续？">
<label>背景信息（可选）</label><textarea id="ctx" placeholder="补充相关背景..."></textarea>
</div>
<div class="section">
<div class="section-title"><span class="dot"></span>四柱 · 情境编码</div>
<div class="tip">把局面拆成四个维度：外部环境、当前局势、自身状态、目标行动。每维选一种力量（五行），评估强度。</div>
<label>年柱 · 外部环境（大背景、行业、趋势）</label>
<div class="row-3"><select id="e0"><option value="木">木·生长力</option><option value="火">火·表现力</option><option value="土" selected>土·承载力</option><option value="金">金·收敛力</option><option value="水">水·流动力</option></select><div style="text-align:center"><div class="range-val" id="v0">5</div><input type="range" id="s0" min="1" max="10" value="5" oninput="v0.textContent=this.value"></div><input type="text" id="d0" placeholder="描述外部环境..."></div>
<label>月柱 · 当前局势（面临的局面、约束条件）</label>
<div class="row-3"><select id="e1"><option value="木">木·生长力</option><option value="火">火·表现力</option><option value="土">土·承载力</option><option value="金" selected>金·收敛力</option><option value="水">水·流动力</option></select><div style="text-align:center"><div class="range-val" id="v1">5</div><input type="range" id="s1" min="1" max="10" value="5" oninput="v1.textContent=this.value"></div><input type="text" id="d1" placeholder="描述当前局势..."></div>
<label>日柱 · 自身状态（能力、资源、心态）</label>
<div class="row-3"><select id="e2"><option value="木" selected>木·生长力</option><option value="火">火·表现力</option><option value="土">土·承载力</option><option value="金">金·收敛力</option><option value="水">水·流动力</option></select><div style="text-align:center"><div class="range-val" id="v2">5</div><input type="range" id="s2" min="1" max="10" value="5" oninput="v2.textContent=this.value"></div><input type="text" id="d2" placeholder="描述自身状态..."></div>
<label>时柱 · 目标行动（想做什么、计划）</label>
<div class="row-3"><select id="e3"><option value="木">木·生长力</option><option value="火" selected>火·表现力</option><option value="土">土·承载力</option><option value="金">金·收敛力</option><option value="水">水·流动力</option></select><div style="text-align:center"><div class="range-val" id="v3">5</div><input type="range" id="s3" min="1" max="10" value="5" oninput="v3.textContent=this.value"></div><input type="text" id="d3" placeholder="描述你的目标..."></div>
</div>
<div class="section">
<div class="section-title"><span class="dot"></span>十神 · 利益相关者</div>
<div class="tip">局面中有哪些关键角色？选角色类型（十神）和力量（五行）。</div>
<div id="shs"></div><button class="btn" onclick="addSh()" style="margin-top:10px">+ 添加角色</button>
</div>
<div class="section">
<div class="section-title"><span class="dot"></span>大运 · 阶段推演</div>
<div class="tip">事情发展拆成几个阶段，每个阶段的主导力量和质量。</div>
<div id="phs"></div><button class="btn" onclick="addPh()" style="margin-top:10px">+ 添加阶段</button>
</div>
<div class="btn-row">
<button class="btn btn-demo" onclick="demo()">📋 加载示例</button>
<button class="btn btn-primary" id="go" onclick="run()">☯ 开始分析</button>
</div>
<div id="result"><div class="ld" id="ld" style="display:none"><div class="sp"></div><p style="margin-top:12px">正在分析...</p></div><div id="rc"></div></div>
</div>
<script>
let sn=0,pn=0;
const RL=['比肩','劫财','正印','偏印','食神','伤官','正财','偏财','正官','七杀'];
const RD={'比肩':'自己','劫财':'竞争者','正印':'正面支持','偏印':'非典型支持','食神':'你的产出','伤官':'你的锋芒','正财':'稳定目标','偏财':'高风险机会','正官':'正面约束','七杀':'负面压力'};
function addSh(d){sn++;const i=sn;const el=document.createElement('div');el.className='sh-item';el.id='sh'+i;
el.innerHTML=`<button class="rm" onclick="document.getElementById('sh${i}').remove()">✕</button><div class="row"><div><label>名称</label><input id="n${i}" value="${d?.name||''}" placeholder="例：老板"></div><div><label>角色</label><select id="r${i}">${RL.map(r=>`<option value="${r}" ${d?.role===r?'selected':''}>${r}·${RD[r]}</option>`).join('')}</select></div></div><div class="row-3"><select id="ce${i}">${'木火土金水'.split('').map(e=>`<option value="${e}" ${d?.element===e?'selected':''}>${e}</option>`).join('')}</select><div style="text-align:center"><div class="range-val" id="cv${i}">${d?.strength||5}</div><input type="range" id="cs${i}" min="1" max="10" value="${d?.strength||5}" oninput="cv${i}.textContent=this.value"></div><input id="cd${i}" value="${d?.description||''}" placeholder="描述..."></div>`;
document.getElementById('shs').appendChild(el)}
function addPh(d){pn++;const i=pn;const el=document.createElement('div');el.className='ph-item';el.id='ph'+i;
el.innerHTML=`<button class="rm" onclick="document.getElementById('ph${i}').remove()">✕</button><div class="row"><div><label>阶段名称</label><input id="pn${i}" value="${d?.name||''}" placeholder="例：起步期"></div><div><label>时间范围</label><input id="pd${i}" value="${d?.duration||''}" placeholder="例：1-3个月"></div></div><div class="row-3"><select id="pe${i}">${'木火土金水'.split('').map(e=>`<option value="${e}" ${d?.element===e?'selected':''}>${e}</option>`).join('')}</select><select id="pq${i}">${['有利','中性','不利'].map(q=>`<option value="${q}" ${d?.quality===q?'selected':''}>${q}</option>`).join('')}</select><input id="pp${i}" value="${d?.description||''}" placeholder="阶段特征..."></div><label>关键行动</label><input id="pa${i}" value="${d?.key_action||''}" placeholder="这个阶段最该做什么...">`;
document.getElementById('phs').appendChild(el)}
function demo(){
q.value='要不要从现在的公司跳槽去创业公司？';ctx.value='在大厂工作3年，薪资稳定但晋升慢。创业公司给了offer，薪资+30%但有风险。';
e0.value='水';s0.value=7;v0.textContent='7';d0.value='经济环境不确定，市场流动性大';
e1.value='金';s1.value=8;v1.textContent='8';d1.value='大厂稳定但天花板明显，规则多空间小';
e2.value='木';s2.value=7;v2.textContent='7';d2.value='有创造力想做事，但被环境压制';
e3.value='火';s3.value=6;v3.textContent='6';d3.value='想要更大的影响力和成长空间';
document.getElementById('shs').innerHTML='';document.getElementById('phs').innerHTML='';sn=0;pn=0;
addSh({name:'大厂体系',role:'正官',element:'金',strength:8,description:'制度约束、晋升缓慢'});
addSh({name:'创业公司CEO',role:'正印',element:'木',strength:7,description:'给你机会和空间'});
addSh({name:'同事小王',role:'劫财',element:'木',strength:5,description:'也在考虑跳槽'});
addSh({name:'家人',role:'偏印',element:'土',strength:6,description:'建议求稳'});
addSh({name:'市场不确定性',role:'七杀',element:'水',strength:7,description:'创业失败概率'});
addPh({name:'现状期',element:'金',duration:'当前',quality:'中性',description:'稳定但无突破',key_action:'盘点核心能力'});
addPh({name:'决策期',element:'木',duration:'1-2个月',quality:'有利',description:'信息充分选择清晰',key_action:'深入聊一次'});
addPh({name:'过渡期',element:'火',duration:'3-6个月',quality:'不利',description:'转换成本高适应期痛苦',key_action:'提前积累人脉和技能'});
addPh({name:'稳定期',element:'土',duration:'半年后',quality:'有利',description:'新环境稳定能力兑现',key_action:'建立不可替代性'})}
function collect(){
const shs=[];document.querySelectorAll('[id^="n"]').forEach(el=>{const i=el.id.slice(1);if(!document.getElementById('n'+i))return;shs.push({name:el.value,role:document.getElementById('r'+i).value,element:document.getElementById('ce'+i).value,strength:+document.getElementById('cs'+i).value,description:document.getElementById('cd'+i).value})});
const phs=[];document.querySelectorAll('[id^="pn"]').forEach(el=>{const i=el.id.slice(2);if(!document.getElementById('pn'+i))return;phs.push({name:el.value,element:document.getElementById('pe'+i).value,document:document.getElementById('pd'+i).value,quality:document.getElementById('pq'+i).value,description:document.getElementById('pp'+i).value,key_action:document.getElementById('pa'+i).value})});
phs.forEach(p=>{p.duration=p.document;delete p.document});
return{question:q.value,context:ctx.value,environment:{element:e0.value,strength:+s0.value,description:d0.value},situation:{element:e1.value,strength:+s1.value,description:d1.value},self_state:{element:e2.value,strength:+s2.value,description:d2.value},goal:{element:e3.value,strength:+s3.value,description:d3.value},stakeholders:shs,phases:phs}}
async function run(){
const d=collect();if(!d.question.trim()){alert('请输入问题');return}
const btn=go;btn.disabled=true;btn.textContent='⏳ 分析中...';result.classList.add('show');ld.style.display='block';rc.innerHTML='';
try{const r=await fetch('/api/analyze',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(d)});
const j=await r.json();ld.style.display='none';if(j.success)render(j);else rc.innerHTML=`<div class="rc"><p style="color:var(--bad)">失败：${j.error}</p></div>`}
catch(e){ld.style.display='none';rc.innerHTML=`<div class="rc"><p style="color:var(--bad)">错误：${e.message}</p></div>`}
btn.disabled=false;btn.textContent='☯ 开始分析'}
function esc(s){return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')}
function render(r){
const b=r.balance,rel=r.relations,ro=r.roles,p=r.phases;let h='';
h+='<div class="rc"><h3>一、五要素平衡分析</h3>';
const bc={'木':'bf-w','火':'bf-f','土':'bf-e','金':'bf-m','水':'bf-a'};
for(const[e,pct]of Object.entries(b['分布']))h+=`<div class="bb"><div class="bl">${e}</div><div class="bg"><div class="bf ${bc[e]}" style="width:${Math.max(pct,2)}%">${pct}%</div></div></div>`;
if(Object.keys(b['过旺']).length)h+=`<p style="color:var(--mid);margin-top:10px;font-size:13px">⚠ 过旺：${Object.keys(b['过旺']).join('、')}</p>`;
if(Object.keys(b['不足']).length)h+=`<p style="color:var(--bad);font-size:13px">⚠ 不足：${Object.keys(b['不足']).join('、')}</p>`;
h+='</div><div class="rc"><h3>二、关系网络分析</h3>';
if(rel.length)rel.slice(0,8).forEach(x=>{h+=`<div class="ri"><span>${x['关系']==='生'?'➕':'⚔️'}</span><span>${x['说明']}</span><span class="rp">力度 ${x['力度']}</span></div>`});
else h+='<p style="color:var(--muted)">各因素相对独立</p>';
h+='</div><div class="rc"><h3>三、角色格局分析</h3>';
for(const[role,info]of Object.entries(ro['角色分布'])){let pp='';for(let i=1;i<=10;i++)pp+=`<div class="p ${i<=info['强度']?'a':''}"></div>`;h+=`<div class="roli"><span class="rb">${role}</span><span>${info['名称']}</span><span style="color:var(--muted);font-size:12px">${info['力量']}·${info['说明']}</span><div class="rs">${pp}</div></div>`}
h+=`<p style="margin-top:12px"><strong>格局：</strong>${ro['格局判断']}</p><p><strong>策略：</strong>${ro['策略建议']}</p></div>`;
if(p['阶段']&&p['阶段'].length){h+='<div class="rc"><h3>四、阶段推演</h3><div class="tl">';
p['阶段'].forEach(x=>{const c=x['质量']==='有利'?'g':(x['质量']==='不利'?'b':'m');h+=`<div class="ti ${c}"><div class="tt">${x['阶段']}·${x['时间']}</div><div class="td">${x['说明']}</div>${x['行动']?`<div class="ta">→ ${x['行动']}</div>`:''}</div>`});
h+=`</div><p style="margin-top:12px"><strong>趋势：</strong>${p['整体趋势']}</p></div>`}
h+='<div class="rc"><h3>综合判断</h3><div class="syn">';
h+=`<p><strong>格局：</strong>${ro['格局判断']}</p><p><strong>策略：</strong>${ro['策略建议']}</p>`;
if(rel.length)h+=`<p><strong>核心力量：</strong>${rel[0]['说明']}</p>`;
if(p.get('阶段'))h+=`<p><strong>时间趋势：</strong>${p['整体趋势']}</p>`;
h+='</div></div>';
h+=`<div class="rc"><h3>完整报告</h3><div class="raw">${esc(r.report)}</div></div>`;
rc.innerHTML=h;result.scrollIntoView({behavior:'smooth'})}
</script>
</body></html>"""

@app.get("/",response_class=HTMLResponse)
async def index(): return HTML

if __name__=="__main__":
    import uvicorn
    print("启动中... 访问 http://localhost:8088")
    uvicorn.run(app,host="0.0.0.0",port=8088)
