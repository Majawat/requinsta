export const getStatusClasses = (status) => {
  const classes = {
    PENDING: 'bg-yellow-900 text-yellow-200',
    APPROVED: 'bg-green-900 text-green-200',
    FULFILLED: 'bg-blue-900 text-blue-200',
    DENIED: 'bg-red-900 text-red-200',
  }
  return classes[status] || 'bg-gray-600 text-gray-200'
}

export const formatDate = (dateString) => {
  if (!dateString) return 'Unknown'
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}
