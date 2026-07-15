import { describe, it, expect } from 'vitest'
import { getSegmentColor, CATEGORY_COLORS_LIGHT, CATEGORY_COLORS_DARK } from '@/utils/colors'

describe('CATEGORY_COLORS_LIGHT', () => {
  it('has 12 distinct colors', () => {
    expect(CATEGORY_COLORS_LIGHT).toHaveLength(12)
    const unique = new Set(CATEGORY_COLORS_LIGHT)
    expect(unique.size).toBe(12)
  })

  it('every color is a valid 6-char hex', () => {
    for (const c of CATEGORY_COLORS_LIGHT) {
      expect(c).toMatch(/^#[0-9A-Fa-f]{6}$/)
    }
  })
})

describe('CATEGORY_COLORS_DARK', () => {
  it('has 12 distinct colors', () => {
    expect(CATEGORY_COLORS_DARK).toHaveLength(12)
    const unique = new Set(CATEGORY_COLORS_DARK)
    expect(unique.size).toBe(12)
  })

  it('every color is a valid 6-char hex', () => {
    for (const c of CATEGORY_COLORS_DARK) {
      expect(c).toMatch(/^#[0-9A-Fa-f]{6}$/)
    }
  })
})

describe('getSegmentColor', () => {
  it('returns segment.color when present', () => {
    expect(getSegmentColor({ color: '#ff0000' })).toBe('#ff0000')
  })

  it('falls back to first palette color when no color is set', () => {
    expect(getSegmentColor({})).toBe(CATEGORY_COLORS_LIGHT[0])
  })

  it('falls back to first palette color when color is empty string', () => {
    expect(getSegmentColor({ color: '' })).toBe(CATEGORY_COLORS_LIGHT[0])
  })
})
