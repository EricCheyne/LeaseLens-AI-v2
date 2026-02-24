from contextvars import ContextVar

current_tenant_id: ContextVar[Optional[int]] = ContextVar('current_tenant_id', default=None)