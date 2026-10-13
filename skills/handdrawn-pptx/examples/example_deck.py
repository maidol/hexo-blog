#!/usr/bin/env python3
"""Example deck showing every component. Copy this file to start a new deck.

usage (via the pipeline):  scripts/build.sh examples/example_deck.py fonts/ZCOOLKuaiLe.ttf out/ example
usage (layout only):       python3 examples/example_deck.py fonts/ZCOOLKuaiLe.ttf out/
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
from handdrawn import Deck  # noqa: E402

font_path, out_dir = sys.argv[1], sys.argv[2]
deck = Deck(font_path, 'ZCOOL KuaiLe', title='手绘风格示例')

# 1. Cover: sketchbook frame, big title, circled tag
s = deck.slide(notes='封面：标题、副标题、对象。讲稿写在 notes 里，不写在页面上。')
s.frame()
s.text(1.1, 2.25, 8.5, '项目季度复盘', 60)
s.ellipse(10.35, 2.85, 1.45, 0.95)
s.text(9.0, 2.48, 2.7, 'Q3', 44, 'center')
s.text(1.1, 3.7, 8.5, '做了什么 · 学到什么 · 下一步', 28)
s.text(1.1, 5.95, 11.0, '全员分享 · 产品 / 研发 / 测试', 16)

# 2. Problem -> fix rows
s = deck.slide('三个问题，三个改法', notes='左边是问题，右边是改法，箭头连接。')
s.text(0.8, 1.45, 4.6, '问题', 16)
s.text(7.5, 1.45, 5.0, '改法', 16)
for i, (a, b) in enumerate([('需求反复变更', '需求冻结后走变更流程'),
                            ('上线经常回滚', '发布前过检查清单'),
                            ('文档找不到', '统一放进知识库')]):
    y = 1.95 + i * 1.3
    s.box(0.8, y, 4.6, 0.9)
    s.text_vc(1.1, y, 4.1, 0.9, a, 20)
    s.arrow((5.65, y + 0.45), (7.2, y + 0.45))
    s.box(7.5, y, 5.0, 0.9)
    s.text_vc(7.8, y, 4.5, 0.9, b, 20)
s.label(0.8, 5.95, 11.73, 0.8, '每个改法都有负责人和完成时间', 18)

# 3. Cards on a column grid + checklist
s = deck.slide('三张卡片，一行结论', notes='deck.columns(3) 给出等宽列。')
for (x, w), (t, body) in zip(deck.columns(3), [('做了什么', '上线 12 个需求\n修复 40 个缺陷'),
                                               ('学到什么', '小步发布更稳\n自动化测试省时间'),
                                               ('下一步', '补齐接口测试\n缩短发布周期')]):
    s.card(x, 1.6, w, 2.4, t, body, title_pt=22, body_pt=16, foot='负责人：待定')
s.checklist(0.85, 4.5, 11.5, ['每张卡片只放一个主题', '正文不超过三行'], 16, 0.2)

# 4. Table + flow
s = deck.slide('表格和流程', notes='table 的第一行是表头；flow 是带箭头的一排方框。')
s.table(0.8, 1.6, [2.0, 5.0, 4.73], 0.75, [
    ['级别', '定义', '处理'],
    ['高', '核心功能不可用', '立即处理'],
    ['中', '主要功能受损，有替代方案', '当天处理'],
    ['低', '界面、文案小问题', '排入后续迭代']], pt=15, head_pt=17)
s.flow(0.8, 5.1, ['发现', '定级', '处理', '复盘'], box_w=2.3, gap=0.85)

# 5. Numbered points + bullets
s = deck.slide('要点与清单', notes='numbered 画圆圈编号；bullets 画手写短横线。')
for i, (a, b) in enumerate([('先对齐目标', '一句话说清要解决什么'), ('再定节奏', '固定发布日，按时发车'), ('最后复盘', '只找原因，不追究个人')]):
    y = 1.7 + i * 1.4
    s.numbered(0.85, y, i + 1)
    s.text(1.6, y + 0.02, 4.8, a, 20)
    s.text(1.6, y + 0.58, 4.8, b, 15)
s.text(7.3, 1.7, 5.2, '注意', 22)
s.bullets(7.35, 2.4, 5.2, ['只用黑白两色', '一页一个重点', '字少，讲稿放备注'], 16, 0.25)

if deck.save(out_dir):
    sys.exit('fix the warnings above, then rebuild')
