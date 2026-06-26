from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class DeploymentProfile:
    mode: str
    title: str
    audience: str
    default_exposure: str
    default_runtime: str
    default_vector_db: str
    default_embedding_model: str
    required_reviews: tuple[str, ...]
    safety_notes: tuple[str, ...]


@dataclass(frozen=True)
class DryRunAnswers:
    mode: str
    project_name: str
    company_name: str
    departments: tuple[str, ...]
    allowed_data_sources: tuple[str, ...]
    forbidden_data: tuple[str, ...]
    remote_access: str
    llm_runtime: str
    vector_db: str
    embedding_model: str
    audit_logging_required: bool
    developer_mode_enabled: bool
    cyber_mode_enabled: bool
    created_at: str


DEPLOYMENT_PROFILES: dict[str, DeploymentProfile] = {
    "local-developer": DeploymentProfile(
        mode="local-developer",
        title="Local Developer Mode",
        audience="Developers testing private AI over approved local files.",
        default_exposure="localhost",
        default_runtime="ollama",
        default_vector_db="qdrant",
        default_embedding_model="bge-small-en",
        required_reviews=("developer", "data owner"),
        safety_notes=(
            "Bind services to localhost by default.",
            "Use approved folders only.",
            "Skip secrets, credentials, and environment files.",
            "Keep developer assistant behavior read-only in v1.",
        ),
    ),
    "small-company": DeploymentProfile(
        mode="small-company",
        title="Small Company Mode",
        audience="Small companies deploying private document search or internal support assistants.",
        default_exposure="vpn-only",
        default_runtime="ollama",
        default_vector_db="qdrant",
        default_embedding_model="bge-small-en",
        required_reviews=("business owner", "security owner", "network owner", "data owner"),
        safety_notes=(
            "Require audit logging before production.",
            "Use role-based collection access.",
            "Review remote access before exposing LAN or VPN services.",
        ),
    ),
    "gpu-server": DeploymentProfile(
        mode="gpu-server",
        title="GPU Server Mode",
        audience="Teams running private AI on a dedicated GPU workstation or server.",
        default_exposure="vpn-only",
        default_runtime="vllm",
        default_vector_db="qdrant",
        default_embedding_model="bge-base-en",
        required_reviews=("security owner", "network owner", "data owner", "ai engineer"),
        safety_notes=(
            "Validate GPU memory against selected model.",
            "Keep model runtime behind the application backend.",
            "Plan audit retention and backups.",
        ),
    ),
    "dgx-enterprise": DeploymentProfile(
        mode="dgx-enterprise",
        title="DGX / Enterprise Mode",
        audience="Enterprise teams using DGX Spark, DGX-class systems, or approved AI servers.",
        default_exposure="enterprise-network",
        default_runtime="nvidia-nim",
        default_vector_db="qdrant",
        default_embedding_model="bge-base-en",
        required_reviews=(
            "business owner",
            "security owner",
            "network owner",
            "data owner",
            "ai engineer",
            "platform owner",
        ),
        safety_notes=(
            "Require named owners for business risk, data, network, and operations.",
            "Use SSO or enterprise identity in production.",
            "Forward audit logs to the approved enterprise destination when required.",
        ),
    ),
    "hybrid-gateway": DeploymentProfile(
        mode="hybrid-gateway",
        title="Hybrid Cloud Gateway Mode",
        audience="Teams that need remote access while keeping private data and inference on-prem.",
        default_exposure="gateway-plus-private-tunnel",
        default_runtime="vllm",
        default_vector_db="qdrant",
        default_embedding_model="bge-base-en",
        required_reviews=("business owner", "security owner", "network owner", "data owner"),
        safety_notes=(
            "Do not store private documents in the cloud gateway by default.",
            "Do not store embeddings in the cloud gateway by default.",
            "Expose only the reviewed gateway path, not the model runtime.",
        ),
    ),
    "dry-run-only": DeploymentProfile(
        mode="dry-run-only",
        title="Dry-Run Planning Only",
        audience="Stakeholders planning private AI before runtime or infrastructure exists.",
        default_exposure="none",
        default_runtime="not-selected",
        default_vector_db="not-selected",
        default_embedding_model="not-selected",
        required_reviews=("business owner", "security owner", "network owner", "data owner"),
        safety_notes=(
            "Do not start containers.",
            "Do not expose ports.",
            "Do not ingest real company data.",
            "Do not create users or apply VPN configuration.",
        ),
    ),
}


MODE_ALIASES = {
    "local": "local-developer",
    "local-dev": "local-developer",
    "local-developer": "local-developer",
    "developer": "local-developer",
    "small": "small-company",
    "small-company": "small-company",
    "gpu": "gpu-server",
    "gpu-server": "gpu-server",
    "dgx": "dgx-enterprise",
    "dgx-spark": "dgx-enterprise",
    "enterprise": "dgx-enterprise",
    "dgx-enterprise": "dgx-enterprise",
    "hybrid": "hybrid-gateway",
    "hybrid-gateway": "hybrid-gateway",
    "dry-run": "dry-run-only",
    "planning": "dry-run-only",
    "dry-run-only": "dry-run-only",
}


def normalize_mode(value: str) -> str:
    normalized = value.strip().lower().replace("_", "-").replace(" ", "-")
    if normalized not in MODE_ALIASES:
        allowed = ", ".join(sorted(DEPLOYMENT_PROFILES))
        raise ValueError(f"unknown mode '{value}'. Allowed modes: {allowed}")
    return MODE_ALIASES[normalized]


def get_profile(mode: str) -> DeploymentProfile:
    return DEPLOYMENT_PROFILES[normalize_mode(mode)]


def default_answers(
    *,
    mode: str,
    project_name: str,
    company_name: str,
    departments: tuple[str, ...] | None = None,
    allowed_data_sources: tuple[str, ...] | None = None,
) -> DryRunAnswers:
    profile = get_profile(mode)
    return DryRunAnswers(
        mode=profile.mode,
        project_name=project_name,
        company_name=company_name,
        departments=departments or ("engineering", "security"),
        allowed_data_sources=allowed_data_sources or ("./examples/sample-company-docs",),
        forbidden_data=(
            ".env files",
            "private keys",
            "API tokens",
            "password stores",
            "unapproved production database dumps",
        ),
        remote_access=profile.default_exposure,
        llm_runtime=profile.default_runtime,
        vector_db=profile.default_vector_db,
        embedding_model=profile.default_embedding_model,
        audit_logging_required=True,
        developer_mode_enabled=profile.mode == "local-developer",
        cyber_mode_enabled=False,
        created_at=datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
    )
