import axios from "axios";
import { QueryResponse, DatabaseSourceInfo } from "../types";

const API_BASE = "http://127.0.0.1:8000";

const client = axios.create({
  baseURL: API_BASE,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 90000,
});

export const api = {
  checkHealth: async () => {
    try {
      const res = await client.get("/health");
      return res.data;
    } catch (e) {
      return { status: "offline", database: { connected: false } };
    }
  },

  sendQuery: async (
    query: string,
    conversationId?: string,
    databaseId?: string
  ): Promise<QueryResponse> => {
    const res = await client.post<QueryResponse>("/query", {
      query,
      conversation_id: conversationId,
      database_id: databaseId && databaseId !== "default" ? databaseId : undefined,
    });
    return res.data;
  },

  getConversationHistory: async (conversationId: string) => {
    const res = await client.get(`/conversation/${conversationId}`);
    return res.data;
  },

  listDatabases: async (): Promise<DatabaseSourceInfo[]> => {
    try {
      const res = await client.get<DatabaseSourceInfo[]>("/database/list");
      return res.data;
    } catch (e) {
      return [];
    }
  },

  uploadDatabase: async (file: File): Promise<DatabaseSourceInfo> => {
    const formData = new FormData();
    formData.append("file", file);

    const res = await client.post<DatabaseSourceInfo>("/database/upload", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    return res.data;
  },

  connectDatabaseUri: async (uri: string, name?: string): Promise<DatabaseSourceInfo> => {
    const res = await client.post<DatabaseSourceInfo>("/database/connect", {
      uri,
      name,
    });
    return res.data;
  },

  getDatabaseSchema: async (databaseId: string) => {
    const res = await client.get(`/database/${databaseId}/schema`);
    return res.data;
  },
};
