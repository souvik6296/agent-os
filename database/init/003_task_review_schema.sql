-- ============================================================
-- Agent OS
-- Task Review Schema
-- Version 0.1
-- ============================================================

-- ============================================================
-- TASK REVIEW REQUIREMENT
-- ============================================================

ALTER TABLE tasks
ADD COLUMN requires_review BOOLEAN NOT NULL DEFAULT FALSE;


-- ============================================================
-- TASK REVIEWS
-- ============================================================

CREATE TABLE task_reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    task_id UUID NOT NULL
        REFERENCES tasks(id)
        ON DELETE CASCADE,

    reviewer_agent_id UUID NOT NULL
        REFERENCES agents(id)
        ON DELETE RESTRICT,

    attempt_number INTEGER NOT NULL,

    result VARCHAR(20) NOT NULL,

    test_cases JSONB NOT NULL DEFAULT '[]'::jsonb,

    test_results JSONB NOT NULL DEFAULT '{}'::jsonb,

    findings JSONB NOT NULL DEFAULT '[]'::jsonb,

    report TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,

    CONSTRAINT task_reviews_attempt_check
        CHECK (attempt_number > 0),

    CONSTRAINT task_reviews_result_check
        CHECK (
            result IN (
                'pass',
                'fail'
            )
        ),

    CONSTRAINT task_reviews_unique_attempt
        UNIQUE (task_id, attempt_number)
);


-- ============================================================
-- INDEXES
-- ============================================================

CREATE INDEX idx_task_reviews_task
    ON task_reviews(task_id);

CREATE INDEX idx_task_reviews_reviewer
    ON task_reviews(reviewer_agent_id);

CREATE INDEX idx_task_reviews_result
    ON task_reviews(result);

