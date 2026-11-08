"""Pure deterministic scheduler for spreading pending assignments across window dates."""

from __future__ import annotations

from datetime import UTC, date, datetime

from app.models.assignment import Assignment
from app.schemas.study_plan import StudyPlanItem

# Daily effort limits in minutes
DAILY_CAP_MINUTES: int = 120

# Point-based effort tiers in minutes
EFFORT_LOW_MAX_POINTS: int = 20
EFFORT_LOW_MINUTES: int = 45
EFFORT_MID_MAX_POINTS: int = 50
EFFORT_MID_MINUTES: int = 90
EFFORT_HIGH_MINUTES: int = 150


def estimate_effort_minutes(max_points: int) -> int:
    """Determine estimated completion effort in minutes based on assignment point value."""
    if max_points <= EFFORT_LOW_MAX_POINTS:
        return EFFORT_LOW_MINUTES
    elif max_points <= EFFORT_MID_MAX_POINTS:
        return EFFORT_MID_MINUTES
    return EFFORT_HIGH_MINUTES


def schedule_pending_assignments(
    pending_assignments: list[Assignment],
    course_title_map: dict[int, str],
    window_dates: list[date],
    now: datetime,
) -> tuple[dict[date, list[StudyPlanItem]], list[StudyPlanItem], list[StudyPlanItem]]:
    """Allocate pending assignments onto study window days respecting caps and deadlines."""
    today = window_dates[0] if window_dates else now.date()

    # Sort key: overdue first (-1 vs 0), then due_at asc, then max_points desc, then id asc
    def sort_key(a: Assignment) -> tuple:
        due = a.due_at if a.due_at.tzinfo is not None else a.due_at.replace(tzinfo=UTC)
        is_ov = due < now
        return (-1 if is_ov else 0, due, -a.max_points, a.id)

    sorted_pending = sorted(pending_assignments, key=sort_key)

    remaining_cap = dict.fromkeys(window_dates, DAILY_CAP_MINUTES)
    day_items: dict[date, list[StudyPlanItem]] = {d: [] for d in window_dates}
    overdue_list: list[StudyPlanItem] = []
    tight_list: list[StudyPlanItem] = []

    for assign in sorted_pending:
        due_utc = (
            assign.due_at if assign.due_at.tzinfo is not None else assign.due_at.replace(tzinfo=UTC)
        )
        due_local = due_utc.astimezone(now.tzinfo) if now.tzinfo is not None else due_utc
        is_ov = due_utc < now
        due_date = due_local.date()
        effort = estimate_effort_minutes(assign.max_points)
        c_title = course_title_map.get(assign.course_id)

        prep_reason = (
            f"Coursework preparation ({effort} min estimated from {assign.max_points} pts)"
        )

        if is_ov:
            # Overdue item: scheduled on today, flagged overdue
            flags = ["overdue"]
            item = StudyPlanItem(
                id=f"assignment-{assign.id}",
                type="assignment",
                title=assign.title,
                course_title=c_title,
                link_path=f"/assignments/{assign.id}",
                due_at=due_local,
                suggested_minutes=effort,
                reason=f"Overdue coursework ({effort} min estimated from {assign.max_points} pts)",
                flags=flags,
            )
            day_items[today].append(item)
            overdue_list.append(item)
            remaining_cap[today] = max(0, remaining_cap[today] - effort)
        else:
            # Upcoming item: spread over days before due date
            days_before = [d for d in window_dates if d < due_date]
            cap_before = sum(remaining_cap[d] for d in days_before)

            if cap_before >= effort:
                # Fits before due date: allocate on earliest days with free capacity
                needed = effort
                for d in days_before:
                    if needed <= 0:
                        break
                    avail = remaining_cap[d]
                    if avail <= 0:
                        continue
                    take = min(needed, avail)
                    remaining_cap[d] -= take
                    needed -= take
                    day_items[d].append(
                        StudyPlanItem(
                            id=f"assignment-{assign.id}-{d.isoformat()}",
                            type="assignment",
                            title=assign.title,
                            course_title=c_title,
                            link_path=f"/assignments/{assign.id}",
                            due_at=due_local,
                            suggested_minutes=take,
                            reason=prep_reason,
                            flags=[],
                        )
                    )
            else:
                # Does not fit before due date: schedule from today, flag tight
                flags = ["tight"]
                tight_list.append(
                    StudyPlanItem(
                        id=f"assignment-{assign.id}",
                        type="assignment",
                        title=assign.title,
                        course_title=c_title,
                        link_path=f"/assignments/{assign.id}",
                        due_at=due_local,
                        suggested_minutes=effort,
                        reason=prep_reason,
                        flags=flags,
                    )
                )
                eligible_days = [d for d in window_dates if d <= due_date]
                needed = effort
                for d in eligible_days:
                    if needed <= 0:
                        break
                    avail = remaining_cap[d]
                    if avail <= 0:
                        continue
                    take = min(needed, avail)
                    remaining_cap[d] -= take
                    needed -= take
                    day_items[d].append(
                        StudyPlanItem(
                            id=f"assignment-{assign.id}-{d.isoformat()}",
                            type="assignment",
                            title=assign.title,
                            course_title=c_title,
                            link_path=f"/assignments/{assign.id}",
                            due_at=due_local,
                            suggested_minutes=take,
                            reason=prep_reason,
                            flags=flags,
                        )
                    )
                if needed > 0 and eligible_days:
                    target_d = eligible_days[-1]
                    day_items[target_d].append(
                        StudyPlanItem(
                            id=f"assignment-{assign.id}-{target_d.isoformat()}-overflow",
                            type="assignment",
                            title=assign.title,
                            course_title=c_title,
                            link_path=f"/assignments/{assign.id}",
                            due_at=due_local,
                            suggested_minutes=needed,
                            reason=prep_reason,
                            flags=flags,
                        )
                    )

    return day_items, overdue_list, tight_list
