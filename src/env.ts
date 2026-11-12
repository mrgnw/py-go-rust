import { defineEnvVars } from '@sveltejs/kit/env';

const optional = (value: string | undefined) => value || undefined;

export const variables = defineEnvVars({
	PUBLIC_TRAKS_SITE: { public: true, static: true, schema: optional },
	PUBLIC_TRAKS_SRC: { public: true, static: true, schema: optional }
});
