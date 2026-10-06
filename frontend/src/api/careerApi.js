import apiClient from './client'

/**
 * POST /api/careers/analyze
 *
 * @param {{
 *   target_career: string,
 *   skills: string[],
 *   experience_level: string,
 *   location?: string,
 * }} payload
 */
export async function analyzeCareer(payload) {
  const response = await apiClient.post('/careers/analyze', payload)
  return response.data
}

/** GET /api/careers -- curated suggestions for a target-career input. */
export async function listSuggestedCareers() {
  const response = await apiClient.get('/careers')
  return response.data
}

export default { analyzeCareer, listSuggestedCareers }
