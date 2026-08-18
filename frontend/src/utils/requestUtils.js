// Status presentation: pill classes + a dot color, keyed by request status.
const STATUS = {
  PENDING:   { label: 'Pending',   classes: 'bg-yellow-500/15 text-yellow-300 ring-1 ring-yellow-500/30', dot: 'bg-yellow-400' },
  APPROVED:  { label: 'Approved',  classes: 'bg-emerald-500/15 text-emerald-300 ring-1 ring-emerald-500/30', dot: 'bg-emerald-400' },
  FULFILLED: { label: 'Available', classes: 'bg-indigo-500/15 text-indigo-300 ring-1 ring-indigo-500/30', dot: 'bg-indigo-400' },
  DENIED:    { label: 'Denied',    classes: 'bg-red-500/15 text-red-300 ring-1 ring-red-500/30', dot: 'bg-red-400' },
}

export const statusMeta = (status) =>
  STATUS[status] || { label: status, classes: 'bg-gray-600/40 text-gray-200 ring-1 ring-gray-500/30', dot: 'bg-gray-400' }

// Backwards-compatible helper (returns just the pill classes).
export const getStatusClasses = (status) => statusMeta(status).classes

const MEDIA_TYPES = {
  book: '📖 Book',
  audiobook: '🎧 Audiobook',
  movie: '🎬 Movie',
  tv_show: '📺 TV Show',
  music: '🎵 Music',
  comic: '📔 Comic',
  other: '📦 Other',
}
export const mediaTypeLabel = (t) => MEDIA_TYPES[t] || t

export const formatDate = (dateString) => {
  if (!dateString) return 'Unknown'
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric', month: 'short', day: 'numeric',
  })
}
