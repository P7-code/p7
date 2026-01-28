import json
import os
from typing import Dict
from jinja2 import Template
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from coze_coding_dev_sdk import LLMClient

from utils.file.file import FileOps
from graphs.state import (
    TenderDocParseInput, TenderDocParseOutput,
    BidDocParseInput, BidDocParseOutput,
    GenerateChecklistInput, GenerateChecklistOutput,
    InvalidItemsCheckInput, InvalidItemsCheckOutput,
    CommercialScoreCheckInput, CommercialScoreCheckOutput,
    TechnicalPlanCheckInput, TechnicalPlanCheckOutput,
    IndicatorResponseCheckInput, IndicatorResponseCheckOutput,
    TechnicalScoreCheckInput, TechnicalScoreCheckOutput,
    BidStructureCheckInput, BidStructureCheckOutput,
    ModificationSummaryInput, ModificationSummaryOutput
)


# ============================================
# 文件解析节点
# ============================================

def tender_doc_parse_node(state: TenderDocParseInput, config: RunnableConfig, runtime: Runtime[Context]) -> TenderDocParseOutput:
    """
    title: 招标文件解析
    desc: 从招标文件中提取文本内容，为后续分析做准备
    integrations: 
    """
    ctx = runtime.context
    try:
        content = FileOps.extract_text(state.tender_file)
        return TenderDocParseOutput(tender_doc_content=content)
    except Exception as e:
        return TenderDocParseOutput(tender_doc_content=f"解析失败: {str(e)}")


def bid_doc_parse_node(state: BidDocParseInput, config: RunnableConfig, runtime: Runtime[Context]) -> BidDocParseOutput:
    """
    title: 投标文件解析
    desc: 从投标文件中提取文本内容，为后续检查做准备
    integrations: 
    """
    ctx = runtime.context
    try:
        content = FileOps.extract_text(state.bid_file)
        return BidDocParseOutput(bid_doc_content=content)
    except Exception as e:
        return BidDocParseOutput(bid_doc_content=f"解析失败: {str(e)}")


# ============================================
# Agent节点函数
# ============================================

def generate_checklist_node(state: GenerateChecklistInput, config: RunnableConfig, runtime: Runtime[Context]) -> GenerateChecklistOutput:
    """
    title: 生成检查清单
    desc: 根据招标文件内容，提取商务要求、商务评分规则、技术评分细则、废标项等关键信息，生成结构化检查清单
    integrations: 大语言模型
    """
    ctx = runtime.context
    
    cfg_file = os.path.join(os.getenv("COZE_WORKSPACE_PATH"), config['metadata']['llm_cfg'])
    with open(cfg_file, 'r', encoding='utf-8') as fd:
        _cfg = json.load(fd)
    
    llm_config = _cfg.get("config", {})
    sp = _cfg.get("sp", "")
    up = _cfg.get("up", "")
    
    up_tpl = Template(up)
    user_prompt_content = up_tpl.render({"tender_doc_content": state.tender_doc_content})
    
    client = LLMClient(ctx=ctx)
    messages = [SystemMessage(content=sp), HumanMessage(content=user_prompt_content)]
    
    resp = client.invoke(
        messages=messages,
        model=llm_config.get("model", "doubao-seed-1-8-251228"),
        temperature=llm_config.get("temperature", 0.3),
        thinking=llm_config.get("thinking", "disabled"),
        max_completion_tokens=llm_config.get("max_completion_tokens", 8192)
    )
    
    content_str = ""
    if isinstance(resp.content, str):
        content_str = resp.content
    elif isinstance(resp.content, list):
        if resp.content and isinstance(resp.content[0], str):
            content_str = " ".join(resp.content)
        else:
            content_str = " ".join(item.get("text", "") for item in resp.content if isinstance(item, dict))
    
    return GenerateChecklistOutput(checklist=content_str)


def invalid_items_check_node(state: InvalidItemsCheckInput, config: RunnableConfig, runtime: Runtime[Context]) -> InvalidItemsCheckOutput:
    """
    title: 废标项检查
    desc: 检查投标文件是否存在废标风险，对比检查清单中的废标要求，给出具体判断结果
    integrations: 大语言模型
    """
    ctx = runtime.context
    
    cfg_file = os.path.join(os.getenv("COZE_WORKSPACE_PATH"), config['metadata']['llm_cfg'])
    with open(cfg_file, 'r', encoding='utf-8') as fd:
        _cfg = json.load(fd)
    
    llm_config = _cfg.get("config", {})
    sp = _cfg.get("sp", "")
    up = _cfg.get("up", "")
    
    up_tpl = Template(up)
    user_prompt_content = up_tpl.render({
        "checklist": state.checklist,
        "bid_doc_content": state.bid_doc_content
    })
    
    client = LLMClient(ctx=ctx)
    messages = [SystemMessage(content=sp), HumanMessage(content=user_prompt_content)]
    
    resp = client.invoke(
        messages=messages,
        model=llm_config.get("model", "doubao-seed-1-8-251228"),
        temperature=llm_config.get("temperature", 0.3),
        thinking=llm_config.get("thinking", "disabled"),
        max_completion_tokens=llm_config.get("max_completion_tokens", 8192)
    )
    
    content_str = ""
    if isinstance(resp.content, str):
        content_str = resp.content
    elif isinstance(resp.content, list):
        if resp.content and isinstance(resp.content[0], str):
            content_str = " ".join(resp.content)
        else:
            content_str = " ".join(item.get("text", "") for item in resp.content if isinstance(item, dict))
    
    return InvalidItemsCheckOutput(invalid_items_check=content_str)


def commercial_score_check_node(state: CommercialScoreCheckInput, config: RunnableConfig, runtime: Runtime[Context]) -> CommercialScoreCheckOutput:
    """
    title: 商务得分点检查
    desc: 根据商务评分规则，检查投标文件商务部分的完整性，估算得分，找出失分点和改进机会
    integrations: 大语言模型
    """
    ctx = runtime.context
    
    cfg_file = os.path.join(os.getenv("COZE_WORKSPACE_PATH"), config['metadata']['llm_cfg'])
    with open(cfg_file, 'r', encoding='utf-8') as fd:
        _cfg = json.load(fd)
    
    llm_config = _cfg.get("config", {})
    sp = _cfg.get("sp", "")
    up = _cfg.get("up", "")
    
    up_tpl = Template(up)
    user_prompt_content = up_tpl.render({
        "checklist": state.checklist,
        "bid_doc_content": state.bid_doc_content
    })
    
    client = LLMClient(ctx=ctx)
    messages = [SystemMessage(content=sp), HumanMessage(content=user_prompt_content)]
    
    resp = client.invoke(
        messages=messages,
        model=llm_config.get("model", "doubao-seed-1-8-251228"),
        temperature=llm_config.get("temperature", 0.3),
        thinking=llm_config.get("thinking", "disabled"),
        max_completion_tokens=llm_config.get("max_completion_tokens", 8192)
    )
    
    content_str = ""
    if isinstance(resp.content, str):
        content_str = resp.content
    elif isinstance(resp.content, list):
        if resp.content and isinstance(resp.content[0], str):
            content_str = " ".join(resp.content)
        else:
            content_str = " ".join(item.get("text", "") for item in resp.content if isinstance(item, dict))
    
    return CommercialScoreCheckOutput(commercial_score_check=content_str)


def technical_plan_check_node(state: TechnicalPlanCheckInput, config: RunnableConfig, runtime: Runtime[Context]) -> TechnicalPlanCheckOutput:
    """
    title: 技术方案检查
    desc: 检查技术方案的完整性、创新性、可行性，评估是否符合技术评分细则，给出改进建议
    integrations: 大语言模型
    """
    ctx = runtime.context
    
    cfg_file = os.path.join(os.getenv("COZE_WORKSPACE_PATH"), config['metadata']['llm_cfg'])
    with open(cfg_file, 'r', encoding='utf-8') as fd:
        _cfg = json.load(fd)
    
    llm_config = _cfg.get("config", {})
    sp = _cfg.get("sp", "")
    up = _cfg.get("up", "")
    
    up_tpl = Template(up)
    user_prompt_content = up_tpl.render({
        "checklist": state.checklist,
        "bid_doc_content": state.bid_doc_content
    })
    
    client = LLMClient(ctx=ctx)
    messages = [SystemMessage(content=sp), HumanMessage(content=user_prompt_content)]
    
    resp = client.invoke(
        messages=messages,
        model=llm_config.get("model", "doubao-seed-1-8-251228"),
        temperature=llm_config.get("temperature", 0.3),
        thinking=llm_config.get("thinking", "disabled"),
        max_completion_tokens=llm_config.get("max_completion_tokens", 8192)
    )
    
    content_str = ""
    if isinstance(resp.content, str):
        content_str = resp.content
    elif isinstance(resp.content, list):
        if resp.content and isinstance(resp.content[0], str):
            content_str = " ".join(resp.content)
        else:
            content_str = " ".join(item.get("text", "") for item in resp.content if isinstance(item, dict))
    
    return TechnicalPlanCheckOutput(technical_plan_check=content_str)


def indicator_response_check_node(state: IndicatorResponseCheckInput, config: RunnableConfig, runtime: Runtime[Context]) -> IndicatorResponseCheckOutput:
    """
    title: 指标与应答检查
    desc: 检查投标文件是否逐条响应了招标文件的技术指标要求，找出遗漏或应答不充分的地方
    integrations: 大语言模型
    """
    ctx = runtime.context
    
    cfg_file = os.path.join(os.getenv("COZE_WORKSPACE_PATH"), config['metadata']['llm_cfg'])
    with open(cfg_file, 'r', encoding='utf-8') as fd:
        _cfg = json.load(fd)
    
    llm_config = _cfg.get("config", {})
    sp = _cfg.get("sp", "")
    up = _cfg.get("up", "")
    
    up_tpl = Template(up)
    user_prompt_content = up_tpl.render({
        "checklist": state.checklist,
        "bid_doc_content": state.bid_doc_content
    })
    
    client = LLMClient(ctx=ctx)
    messages = [SystemMessage(content=sp), HumanMessage(content=user_prompt_content)]
    
    resp = client.invoke(
        messages=messages,
        model=llm_config.get("model", "doubao-seed-1-8-251228"),
        temperature=llm_config.get("temperature", 0.3),
        thinking=llm_config.get("thinking", "disabled"),
        max_completion_tokens=llm_config.get("max_completion_tokens", 8192)
    )
    
    content_str = ""
    if isinstance(resp.content, str):
        content_str = resp.content
    elif isinstance(resp.content, list):
        if resp.content and isinstance(resp.content[0], str):
            content_str = " ".join(resp.content)
        else:
            content_str = " ".join(item.get("text", "") for item in resp.content if isinstance(item, dict))
    
    return IndicatorResponseCheckOutput(indicator_response_check=content_str)


def technical_score_check_node(state: TechnicalScoreCheckInput, config: RunnableConfig, runtime: Runtime[Context]) -> TechnicalScoreCheckOutput:
    """
    title: 技术得分点检测
    desc: 根据技术指标与应答情况，结合招标文件中的技术要求，进行技术得分点检测，检查是否覆盖全部技术应答内容，是否有遗漏缺项，是否有应答不充分或者应答错误等影响技术评分的情况
    integrations: 大语言模型
    """
    ctx = runtime.context
    
    cfg_file = os.path.join(os.getenv("COZE_WORKSPACE_PATH"), config['metadata']['llm_cfg'])
    with open(cfg_file, 'r', encoding='utf-8') as fd:
        _cfg = json.load(fd)
    
    llm_config = _cfg.get("config", {})
    sp = _cfg.get("sp", "")
    up = _cfg.get("up", "")
    
    up_tpl = Template(up)
    user_prompt_content = up_tpl.render({
        "checklist": state.checklist,
        "bid_doc_content": state.bid_doc_content,
        "indicator_response_check": state.indicator_response_check
    })
    
    client = LLMClient(ctx=ctx)
    messages = [SystemMessage(content=sp), HumanMessage(content=user_prompt_content)]
    
    resp = client.invoke(
        messages=messages,
        model=llm_config.get("model", "doubao-seed-1-8-251228"),
        temperature=llm_config.get("temperature", 0.3),
        thinking=llm_config.get("thinking", "disabled"),
        max_completion_tokens=llm_config.get("max_completion_tokens", 8192)
    )
    
    content_str = ""
    if isinstance(resp.content, str):
        content_str = resp.content
    elif isinstance(resp.content, list):
        if resp.content and isinstance(resp.content[0], str):
            content_str = " ".join(resp.content)
        else:
            content_str = " ".join(item.get("text", "") for item in resp.content if isinstance(item, dict))
    
    return TechnicalScoreCheckOutput(technical_score_check=content_str)


def bid_structure_check_node(state: BidStructureCheckInput, config: RunnableConfig, runtime: Runtime[Context]) -> BidStructureCheckOutput:
    """
    title: 投标文件结构检查
    desc: 根据投标文件中对于商务部分与技术部分的模板要求，对投标文件整体目录结构进行检查，是否有缺失项，是否存在目录与内容排布不合理等影响专家阅读标书快速对应得分点等问题
    integrations: 大语言模型
    """
    ctx = runtime.context
    
    cfg_file = os.path.join(os.getenv("COZE_WORKSPACE_PATH"), config['metadata']['llm_cfg'])
    with open(cfg_file, 'r', encoding='utf-8') as fd:
        _cfg = json.load(fd)
    
    llm_config = _cfg.get("config", {})
    sp = _cfg.get("sp", "")
    up = _cfg.get("up", "")
    
    up_tpl = Template(up)
    user_prompt_content = up_tpl.render({
        "tender_doc_content": state.tender_doc_content,
        "bid_doc_content": state.bid_doc_content,
        "checklist": state.checklist
    })
    
    client = LLMClient(ctx=ctx)
    messages = [SystemMessage(content=sp), HumanMessage(content=user_prompt_content)]
    
    resp = client.invoke(
        messages=messages,
        model=llm_config.get("model", "doubao-seed-1-8-251228"),
        temperature=llm_config.get("temperature", 0.3),
        thinking=llm_config.get("thinking", "disabled"),
        max_completion_tokens=llm_config.get("max_completion_tokens", 8192)
    )
    
    content_str = ""
    if isinstance(resp.content, str):
        content_str = resp.content
    elif isinstance(resp.content, list):
        if resp.content and isinstance(resp.content[0], str):
            content_str = " ".join(resp.content)
        else:
            content_str = " ".join(item.get("text", "") for item in resp.content if isinstance(item, dict))
    
    return BidStructureCheckOutput(bid_structure_check=content_str)


def modification_summary_node(state: ModificationSummaryInput, config: RunnableConfig, runtime: Runtime[Context]) -> ModificationSummaryOutput:
    """
    title: 修改建议汇总
    desc: 汇总所有检查结果，按优先级排序，生成完整的修改清单和详细修改意见
    integrations: 大语言模型
    """
    ctx = runtime.context
    
    cfg_file = os.path.join(os.getenv("COZE_WORKSPACE_PATH"), config['metadata']['llm_cfg'])
    with open(cfg_file, 'r', encoding='utf-8') as fd:
        _cfg = json.load(fd)
    
    llm_config = _cfg.get("config", {})
    sp = _cfg.get("sp", "")
    up = _cfg.get("up", "")
    
    up_tpl = Template(up)
    user_prompt_content = up_tpl.render({
        "invalid_items_check": state.invalid_items_check,
        "commercial_score_check": state.commercial_score_check,
        "technical_plan_check": state.technical_plan_check,
        "indicator_response_check": state.indicator_response_check,
        "technical_score_check": state.technical_score_check,
        "bid_structure_check": state.bid_structure_check
    })
    
    client = LLMClient(ctx=ctx)
    messages = [SystemMessage(content=sp), HumanMessage(content=user_prompt_content)]
    
    resp = client.invoke(
        messages=messages,
        model=llm_config.get("model", "doubao-seed-1-8-251228"),
        temperature=llm_config.get("temperature", 0.3),
        thinking=llm_config.get("thinking", "disabled"),
        max_completion_tokens=llm_config.get("max_completion_tokens", 16384)
    )
    
    content_str = ""
    if isinstance(resp.content, str):
        content_str = resp.content
    elif isinstance(resp.content, list):
        if resp.content and isinstance(resp.content[0], str):
            content_str = " ".join(resp.content)
        else:
            content_str = " ".join(item.get("text", "") for item in resp.content if isinstance(item, dict))
    
    return ModificationSummaryOutput(final_modification_suggestions=content_str)
