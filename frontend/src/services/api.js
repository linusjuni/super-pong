import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8000",
});

export const playerApi = {
  list: () => api.get("/players/").then((r) => r.data),
  search: (q) => api.get("/players/search", { params: { q } }).then((r) => r.data),
  create: (data) => api.post("/players/", data).then((r) => r.data),
  get: (id) => api.get(`/players/${id}`).then((r) => r.data),
};

export const tournamentApi = {
  list: () => api.get("/tournaments/").then((r) => r.data),
  create: (data) => api.post("/tournaments/", data).then((r) => r.data),
  get: (id) => api.get(`/tournaments/${id}`).then((r) => r.data),
  delete: (id) => api.delete(`/tournaments/${id}`),
  getTeams: (id) => api.get(`/tournaments/${id}/teams`).then((r) => r.data),
  getGames: (id) => api.get(`/tournaments/${id}/games`).then((r) => r.data),
};

export const teamApi = {
  create: (tournamentId, data) =>
    api.post(`/tournaments/${tournamentId}/teams`, data).then((r) => r.data),
  update: (id, data) => api.put(`/teams/${id}`, data).then((r) => r.data),
  delete: (id) => api.delete(`/teams/${id}`),
};

export const gameApi = {
  create: (tournamentId, data) =>
    api.post(`/tournaments/${tournamentId}/games`, data).then((r) => r.data),
  get: (id) => api.get(`/games/${id}`).then((r) => r.data),
  update: (id, data) => api.put(`/games/${id}`, data).then((r) => r.data),
  delete: (id) => api.delete(`/games/${id}`),
};

export const shotApi = {
  create: (gameId, data) =>
    api.post(`/games/${gameId}/shots`, data).then((r) => r.data),
  list: (gameId) => api.get(`/games/${gameId}/shots`).then((r) => r.data),
  delete: (id) => api.delete(`/shots/${id}`),
};
