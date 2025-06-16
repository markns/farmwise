import { Parser } from '@json2csv/plainjs'
import { flatten } from '@json2csv/transforms'

/**
 * Toggle fullscreen mode for the current document
 */
export const toggleFullScreen = (): void => {
  const doc = window.document
  const docEl = doc.documentElement

  const requestFullScreen = 
    docEl.requestFullscreen ||
    (docEl as any).mozRequestFullScreen ||
    (docEl as any).webkitRequestFullScreen ||
    (docEl as any).msRequestFullscreen

  const cancelFullScreen = 
    doc.exitFullscreen ||
    (doc as any).mozCancelFullScreen ||
    (doc as any).webkitExitFullscreen ||
    (doc as any).msExitFullscreen

  if (
    !doc.fullscreenElement &&
    !(doc as any).mozFullScreenElement &&
    !(doc as any).webkitFullscreenElement &&
    !(doc as any).msFullscreenElement
  ) {
    requestFullScreen?.call(docEl)
  } else {
    cancelFullScreen?.call(doc)
  }
}

/**
 * Export data as CSV file with automatic field detection
 */
export const exportCSV = (items: any[], fileName: string): void => {
  if (!items || items.length === 0) {
    console.warn('No data to export')
    return
  }

  try {
    const json2csvParser = new Parser({ transforms: [flatten()] })
    const csv = json2csvParser.parse(items)
    downloadCSV(csv, fileName)
  } catch (error) {
    console.error('Error exporting CSV:', error)
  }
}

/**
 * Export data as CSV file with specified field order
 */
export const exportCSVOrdered = (items: any[], fileName: string, fieldOrder: string[]): void => {
  if (!items || items.length === 0) {
    console.warn('No data to export')
    return
  }

  try {
    const json2csvParser = new Parser({ 
      transforms: [flatten()], 
      fields: fieldOrder 
    })
    const csv = json2csvParser.parse(items)
    downloadCSV(csv, fileName)
  } catch (error) {
    console.error('Error exporting CSV:', error)
  }
}

/**
 * Helper function to trigger CSV file download
 */
const downloadCSV = (csv: string, fileName: string): void => {
  const data = 'data:text/csv;charset=utf-8,' + encodeURIComponent(csv)
  const link = document.createElement('a')
  link.setAttribute('href', data)
  link.setAttribute('download', fileName.endsWith('.csv') ? fileName : `${fileName}.csv`)
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

/**
 * Format file size in human readable format
 */
export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes'
  
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

/**
 * Debounce function to limit how often a function can be called
 */
export const debounce = <T extends (...args: any[]) => any>(
  func: T,
  wait: number
): ((...args: Parameters<T>) => void) => {
  let timeout: ReturnType<typeof setTimeout>
  
  return (...args: Parameters<T>) => {
    clearTimeout(timeout)
    timeout = setTimeout(() => func(...args), wait)
  }
}

/**
 * Deep clone an object
 */
export const deepClone = <T>(obj: T): T => {
  if (obj === null || typeof obj !== 'object') return obj
  if (obj instanceof Date) return new Date(obj.getTime()) as unknown as T
  if (obj instanceof Array) return obj.map(item => deepClone(item)) as unknown as T
  if (typeof obj === 'object') {
    const copy = {} as { [key: string]: any }
    Object.keys(obj).forEach(key => {
      copy[key] = deepClone((obj as { [key: string]: any })[key])
    })
    return copy as T
  }
  return obj
}

/**
 * Get nested object property safely
 */
export const getNestedProperty = (obj: any, path: string): any => {
  return path.split('.').reduce((current, key) => current?.[key], obj)
}

/**
 * Set nested object property safely
 */
export const setNestedProperty = (obj: any, path: string, value: any): void => {
  const keys = path.split('.')
  const lastKey = keys.pop()
  
  if (!lastKey) return
  
  const target = keys.reduce((current, key) => {
    if (!(key in current)) {
      current[key] = {}
    }
    return current[key]
  }, obj)
  
  target[lastKey] = value
}

/**
 * Generate a random ID
 */
export const generateId = (): string => {
  return Date.now().toString(36) + Math.random().toString(36).substr(2)
}

/**
 * Check if a value is empty (null, undefined, empty string, empty array, empty object)
 */
export const isEmpty = (value: any): boolean => {
  if (value === null || value === undefined) return true
  if (typeof value === 'string') return value.trim() === ''
  if (Array.isArray(value)) return value.length === 0
  if (typeof value === 'object') return Object.keys(value).length === 0
  return false
}

/**
 * Capitalize the first letter of a string
 */
export const capitalize = (str: string): string => {
  return str.charAt(0).toUpperCase() + str.slice(1)
}

/**
 * Convert camelCase to kebab-case
 */
export const camelToKebab = (str: string): string => {
  return str.replace(/([a-z0-9]|(?=[A-Z]))([A-Z])/g, '$1-$2').toLowerCase()
}

/**
 * Convert kebab-case to camelCase
 */
export const kebabToCamel = (str: string): string => {
  return str.replace(/-([a-z])/g, (_, letter) => letter.toUpperCase())
}

export default {
  toggleFullScreen,
  exportCSV,
  exportCSVOrdered,
  formatFileSize,
  debounce,
  deepClone,
  getNestedProperty,
  setNestedProperty,
  generateId,
  isEmpty,
  capitalize,
  camelToKebab,
  kebabToCamel,
}