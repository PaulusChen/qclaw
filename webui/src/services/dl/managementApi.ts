// 深度学习模型管理 API 服务
import axios from 'axios';
import type {
  ModelInfo,
  ModelsListResponse,
  ModelDetailResponse,
  ActivateModelRequest,
  ArchiveModelRequest,
  DeleteModelRequest,
  ExportModelRequest,
  ExportModelResponse,
  ImportModelResponse,
  CompareModelsRequest,
  CompareModelsResponse,
} from '../../types/dl';

const API_BASE = '/api/v1/dl';

export const managementApi = {
  /**
   * 获取模型列表
   */
  async getModels(): Promise<ModelsListResponse> {
    const response = await axios.get(`${API_BASE}/models`);
    return response.data;
  },

  /**
   * 获取模型详情
   */
  async getModelDetail(version: string): Promise<ModelDetailResponse> {
    const response = await axios.get(`${API_BASE}/models/${encodeURIComponent(version)}`);
    return response.data;
  },

  /**
   * 激活模型
   */
  async activateModel(version: string): Promise<void> {
    const request: ActivateModelRequest = { version };
    await axios.post(`${API_BASE}/models/${encodeURIComponent(version)}/activate`, request);
  },

  /**
   * 归档模型
   */
  async archiveModel(version: string): Promise<void> {
    const request: ArchiveModelRequest = { version };
    await axios.post(`${API_BASE}/models/${encodeURIComponent(version)}/archive`, request);
  },

  /**
   * 删除模型
   */
  async deleteModel(version: string): Promise<void> {
    const request: DeleteModelRequest = { version, confirm: true };
    await axios.delete(`${API_BASE}/models/${encodeURIComponent(version)}`, { data: request });
  },

  /**
   * 导出模型
   */
  async exportModel(version: string, format: 'onnx' | 'torchscript' | 'safetensors' = 'torchscript'): Promise<ExportModelResponse> {
    const request: ExportModelRequest = { version, format };
    const response = await axios.post(`${API_BASE}/models/${encodeURIComponent(version)}/export`, request);
    return response.data;
  },

  /**
   * 导入模型
   */
  async importModel(
    file: File,
    metadata?: { name?: string; description?: string; tags?: string[] }
  ): Promise<ImportModelResponse> {
    const formData = new FormData();
    formData.append('file', file);
    if (metadata) {
      formData.append('metadata', JSON.stringify(metadata));
    }

    const response = await axios.post(`${API_BASE}/models/import`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  /**
   * 对比模型
   */
  async compareModels(versions: string[]): Promise<CompareModelsResponse> {
    const request: CompareModelsRequest = { versions };
    const response = await axios.get(`${API_BASE}/models/compare`, {
      params: { versions: versions.join(',') },
    });
    return response.data;
  },

  /**
   * 更新模型元数据
   */
  async updateModelMetadata(
    version: string,
    metadata: { name?: string; description?: string; tags?: string[] }
  ): Promise<void> {
    await axios.put(`${API_BASE}/models/${encodeURIComponent(version)}/metadata`, metadata);
  },
};

export default managementApi;
