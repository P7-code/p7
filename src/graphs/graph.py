from langgraph.graph import StateGraph, END

from graphs.state import (
    GlobalState,
    GraphInput,
    GraphOutput
)

from graphs.node import (
    tender_doc_parse_node,
    bid_doc_parse_node,
    generate_checklist_node,
    invalid_items_check_node,
    commercial_score_check_node,
    technical_plan_check_node,
    indicator_response_check_node,
    technical_score_check_node,
    bid_structure_check_node,
    modification_summary_node
)

# 创建状态图，指定入参和出参
builder = StateGraph(GlobalState, input_schema=GraphInput, output_schema=GraphOutput)

# 添加节点
builder.add_node("tender_doc_parse", tender_doc_parse_node)
builder.add_node("bid_doc_parse", bid_doc_parse_node)
builder.add_node("generate_checklist", generate_checklist_node, 
                metadata={"type": "agent", "llm_cfg": "config/generate_checklist_cfg.json"})
builder.add_node("invalid_items_check", invalid_items_check_node,
                metadata={"type": "agent", "llm_cfg": "config/invalid_items_check_cfg.json"})
builder.add_node("commercial_score_check", commercial_score_check_node,
                metadata={"type": "agent", "llm_cfg": "config/commercial_score_check_cfg.json"})
builder.add_node("technical_plan_check", technical_plan_check_node,
                metadata={"type": "agent", "llm_cfg": "config/technical_plan_check_cfg.json"})
builder.add_node("indicator_response_check", indicator_response_check_node,
                metadata={"type": "agent", "llm_cfg": "config/indicator_response_check_cfg.json"})
builder.add_node("technical_score_check", technical_score_check_node,
                metadata={"type": "agent", "llm_cfg": "config/technical_score_check_cfg.json"})
builder.add_node("bid_structure_check", bid_structure_check_node,
                metadata={"type": "agent", "llm_cfg": "config/bid_structure_check_cfg.json"})
builder.add_node("modification_summary", modification_summary_node,
                metadata={"type": "agent", "llm_cfg": "config/modification_summary_cfg.json"})

# 设置入口点
builder.set_entry_point("tender_doc_parse")

# 添加边 - 采用清晰的串行+并行结构
# 第一阶段：解析文件（串行）
builder.add_edge("tender_doc_parse", "bid_doc_parse")

# 第二阶段：生成检查清单（串行）
builder.add_edge("bid_doc_parse", "generate_checklist")

# 第三阶段：并行检查
# generate_checklist完成后，启动六个并行检查
builder.add_edge("generate_checklist", "invalid_items_check")
builder.add_edge("generate_checklist", "commercial_score_check")
builder.add_edge("generate_checklist", "technical_plan_check")
builder.add_edge("generate_checklist", "indicator_response_check")
builder.add_edge("generate_checklist", "technical_score_check")
builder.add_edge("generate_checklist", "bid_structure_check")

# 第四阶段：汇总修改建议
# 六个检查节点都完成后，汇总到modification_summary
builder.add_edge(["invalid_items_check", "commercial_score_check", "technical_plan_check", 
                "indicator_response_check", "technical_score_check", "bid_structure_check"], 
                "modification_summary")

# 添加边 - 汇总完成后结束
builder.add_edge("modification_summary", END)

# 编译图
main_graph = builder.compile()
