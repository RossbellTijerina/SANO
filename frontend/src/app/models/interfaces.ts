export interface Usuario {
  id: number;
  username: string;
  nombre_completo: string;
  rol: 'Administrador' | 'Capturista';
  activo: boolean;
  fecha_creacion?: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  usuario: Usuario;
}

export interface Oficio {
  id: number;
  anio: number;
  folio: number;
  expediente: string;
  solicitante: string;
  asunto: string;
  fecha: string;
  funcionario_id: number | null;
  funcionario_nombre: string | null;
  estado: 'ACTIVO' | 'CANCELADO';
  motivo_cancelacion: string | null;
  creado_por: number;
  creado_por_nombre: string | null;
  fecha_creacion: string;
  fecha_modificacion: string;
}

export interface OficioListResponse {
  oficios: Oficio[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

export interface BusquedaResponse {
  oficios: Oficio[];
  total: number;
}

export interface Funcionario {
  id: number;
  nombre: string;
  cargo: string;
  departamento: string;
  activo: boolean;
  fecha_creacion?: string;
}

export interface Estadisticas {
  totales: {
    total: number;
    activos: number;
    cancelados: number;
    hoy: number;
  };
  por_mes: { mes: number; cantidad: number }[];
  ultimos_oficios: Oficio[];
  anios_disponibles: number[];
  anio_actual: number;
}
