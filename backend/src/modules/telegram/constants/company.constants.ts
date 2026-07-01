/**
 * Static company facts referenced by handlers (location pin, etc.).
 * Replace with real production values / move to configuration as needed.
 */
export const CompanyLocation = {
  latitude: 41.311081,
  longitude: 69.240562,
} as const;

/**
 * Company contact endpoints referenced by content pages. These are values, not
 * copy, so they live here rather than in the i18n catalogs.
 */
export const CompanyContacts = {
  website: 'https://teplolux.example.com',
  catalog: 'https://teplolux.example.com/catalog',
  phone: '+998000000000',
} as const;
