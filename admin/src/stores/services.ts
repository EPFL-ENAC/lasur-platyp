import { defineStore } from 'pinia'
import { api } from 'src/boot/api'
import type { Company, Campaign, Participant } from 'src/models'
import type { Query } from 'src/components/models'

const authStore = useAuthStore()

export class Service<Type extends Company | Campaign | Participant> {
  constructor(
    public entityType: Type,
    public entityName: string,
  ) {}

  async create(payload: Type) {
    if (!authStore.isAuthenticated) return Promise.reject('Not authenticated')
    return authStore.updateToken().then(() => {
      const config = {
        headers: {
          Authorization: `Bearer ${authStore.accessToken}`,
        },
      }
      return api.post(`/${this.entityName}/`, payload, config)
    })
  }

  async get(id: string): Promise<Type> {
    if (!authStore.isAuthenticated) return Promise.reject('Not authenticated')
    return authStore.updateToken().then(() => {
      const config = {
        headers: {
          Authorization: `Bearer ${authStore.accessToken}`,
        },
      }
      return api.get(`/${this.entityName}/${id}`, config).then((res) => res.data)
    })
  }

  async find(query: Query | undefined) {
    if (!authStore.isAuthenticated) return Promise.reject('Not authenticated')
    const range = [query?.$skip || 0, query?.$limit || 10 - 1]
    const sort = query?.$sort ? [query?.$sort[0], query?.$sort[1] ? 'DESC' : 'ASC'] : ['id', 'ASC']
    return authStore.updateToken().then(() => {
      return api
        .get(`/${this.entityName}/`, {
          headers: {
            Authorization: `Bearer ${authStore.accessToken}`,
          },
          params: {
            select: query?.$select ? JSON.stringify(query?.$select) : undefined,
            range: JSON.stringify(range),
            sort: JSON.stringify(sort),
            filter: JSON.stringify(query?.filter),
          },
        })
        .then((res) => res.data)
    })
  }

  async update(id: string | number, payload: Type) {
    if (!authStore.isAuthenticated) return Promise.reject('Not authenticated')
    delete payload.created_at
    delete payload.updated_at
    delete payload.created_by
    delete payload.updated_by
    return authStore.updateToken().then(() => {
      const config = {
        headers: {
          Authorization: `Bearer ${authStore.accessToken}`,
        },
      }
      return api.put(`/${this.entityName}/${id}`, payload, config)
    })
  }

  async remove(id: string | number) {
    if (!authStore.isAuthenticated) return Promise.reject('Not authenticated')
    return authStore.updateToken().then(() => {
      const config = {
        headers: {
          Authorization: `Bearer ${authStore.accessToken}`,
        },
      }
      return api.delete(`/${this.entityName}/${id}`, config)
    })
  }
}

export const useServices = defineStore('services', () => {
  function make(entityName: string): Service<Company | Campaign | Participant> {
    let entityType
    switch (entityName) {
      case 'company':
        entityType = {} as Company
        break
      case 'campaign':
        entityType = {} as Campaign
        break
      case 'participant':
        entityType = {} as Participant
        break
    }
    if (!entityType) {
      throw new Error('Invalid entity name: ' + entityName)
    }
    return new Service(entityType, entityName)
  }

  return {
    make,
  }
})
