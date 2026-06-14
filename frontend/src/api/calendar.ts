import client from './client'

export const calendarApi = {
  getMonth(year: number, month: number) {
    return client.get('/calendar', { params: { year, month } }).then(r => r.data.data)
  },
  getWeek(start: string, end: string) {
    return client.get('/calendar/week', { params: { start, end } }).then(r => r.data.data)
  },
}
