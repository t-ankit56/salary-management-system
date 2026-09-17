/** Report endpoint calls. */

import { apiFetch } from './client'

export function getReport(name, asOf) {
  return apiFetch(`/api/reports/${name}/?as_of=${asOf}`)
}
