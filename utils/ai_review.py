"""
打卡目标的「AI 自动审核」——当前为规则启发式(rule-based)实现。

设计成一个独立函数 ai_review_target(target) -> (approved, reason)，
管理端路由直接调用即可。以后若要换成真正的大模型(如 Claude API)，
只需保持相同的入参/返回值，替换函数内部实现即可，路由层无需改动。
"""
from modules.target import Target

# 敏感/违规关键词，命中则直接驳回（按需扩充）
BANNED_WORDS = [
    "赌博", "博彩", "色情", "毒品", "诈骗", "暴力", "传销", "代刷", "外挂",
]

# 目标名称长度限制
MIN_NAME_LEN = 2
MAX_NAME_LEN = 50

# 目标持续天数的合理区间（开始到截止）
MIN_DURATION_DAYS = 1
MAX_DURATION_DAYS = 365


def ai_review_target(target: Target) -> tuple[bool, str]:
    """对单个打卡目标做规则启发式审核。

    返回 (approved, reason):
      - approved: True 表示通过, False 表示驳回
      - reason: 审核意见（通过原因或驳回原因），会写入 target.audit_reason
    """
    name = (target.name or "").strip()

    # 1) 名称非空
    if not name:
        return False, "目标名称为空"

    # 2) 名称长度
    if len(name) < MIN_NAME_LEN:
        return False, f"目标名称过短(至少{MIN_NAME_LEN}个字符)"
    if len(name) > MAX_NAME_LEN:
        return False, f"目标名称过长(最多{MAX_NAME_LEN}个字符)"

    # 3) 敏感词检测
    for word in BANNED_WORDS:
        if word in name:
            return False, f"目标名称包含违规内容: {word}"

    # 4) 时间合理性：开始必须早于截止
    if target.start_time is None or target.deadline_time is None:
        return False, "目标缺少开始时间或截止时间"
    if target.start_time >= target.deadline_time:
        return False, "开始时间必须早于截止时间"

    # 5) 持续天数在合理区间内
    duration_days = (target.deadline_time - target.start_time).days
    if duration_days < MIN_DURATION_DAYS:
        return False, "目标周期过短(至少1天)"
    if duration_days > MAX_DURATION_DAYS:
        return False, f"目标周期过长(最多{MAX_DURATION_DAYS}天)"

    # 6) 提醒时间应落在开始与截止之间
    if target.remind_time is not None and not (
        target.start_time <= target.remind_time <= target.deadline_time
    ):
        return False, "提醒时间需在开始时间与截止时间之间"

    return True, "规则校验通过, 内容合规"
