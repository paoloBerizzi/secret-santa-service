from datetime import date

from sqlalchemy import CheckConstraint, ForeignKey, ForeignKeyConstraint, String, UniqueConstraint, true
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Event(Base):
    __tablename__ = 'events'
    __table_args__ = (
        CheckConstraint('budget >= 0', name='nonnegative_budget'),
        CheckConstraint("state IN ('draft', 'drawn', 'locked')", name='valid_draw_state'),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    icon: Mapped[str] = mapped_column(String(20), default='fox', server_default='fox')
    budget: Mapped[int]
    currency: Mapped[str] = mapped_column(String(3))
    exchange_date: Mapped[date]
    notes: Mapped[str] = mapped_column(String(2000), default='')
    admin_digest: Mapped[str] = mapped_column(String(64), unique=True)
    no_reciprocal: Mapped[bool] = mapped_column(default=False)
    wishlist_enabled: Mapped[bool] = mapped_column(default=True, server_default=true())
    state: Mapped[str] = mapped_column(String(8), default='draft')
    revision: Mapped[int] = mapped_column(default=0)
    draw_nonce: Mapped[str | None] = mapped_column(String(64))


class Participant(Base):
    __tablename__ = 'participants'
    __table_args__ = (UniqueConstraint('event_id', 'id'),)

    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey('events.id', ondelete='CASCADE'))
    name: Mapped[str] = mapped_column(String(100))
    wishlist: Mapped[str] = mapped_column(String(2000), default='')
    reveal_digest: Mapped[str | None] = mapped_column(String(64), unique=True)


class Subgroup(Base):
    __tablename__ = 'subgroups'
    __table_args__ = (UniqueConstraint('event_id', 'id'), UniqueConstraint('event_id', 'name'))

    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey('events.id', ondelete='CASCADE'))
    name: Mapped[str] = mapped_column(String(100))
    no_intra_exchange: Mapped[bool] = mapped_column(default=True)


def participant_fk(column: str) -> ForeignKeyConstraint:
    return ForeignKeyConstraint(
        ['event_id', column], ['participants.event_id', 'participants.id'], ondelete='CASCADE',
    )


class SubgroupMember(Base):
    __tablename__ = 'subgroup_members'
    __table_args__ = (
        ForeignKeyConstraint(
            ['event_id', 'subgroup_id'], ['subgroups.event_id', 'subgroups.id'], ondelete='CASCADE',
        ),
        participant_fk('participant_id'),
    )

    event_id: Mapped[int] = mapped_column(primary_key=True)
    subgroup_id: Mapped[int] = mapped_column(primary_key=True)
    participant_id: Mapped[int] = mapped_column(primary_key=True)


class ExclusionRule(Base):
    __tablename__ = 'exclusion_rules'
    __table_args__ = (
        participant_fk('giver_id'), participant_fk('receiver_id'),
        UniqueConstraint('event_id', 'giver_id', 'receiver_id'),
        CheckConstraint('giver_id <> receiver_id', name='no_self_exclusion'),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[int]
    giver_id: Mapped[int]
    receiver_id: Mapped[int]


class Assignment(Base):
    __tablename__ = 'assignments'
    __table_args__ = (
        participant_fk('giver_id'), participant_fk('receiver_id'),
        UniqueConstraint('event_id', 'receiver_id'),
        CheckConstraint('giver_id <> receiver_id', name='no_self_assignment'),
    )

    event_id: Mapped[int] = mapped_column(primary_key=True)
    giver_id: Mapped[int] = mapped_column(primary_key=True)
    receiver_id: Mapped[int]