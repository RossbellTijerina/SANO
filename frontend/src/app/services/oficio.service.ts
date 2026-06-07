import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { Oficio, OficioListResponse, BusquedaResponse, Estadisticas } from '../models/interfaces';

@Injectable({ providedIn: 'root' })
export class OficioService {
  private apiUrl = `${environment.apiUrl}/oficios`;

  constructor(private http: HttpClient) {}

  listar(anio?: number, page: number = 1, perPage: number = 20): Observable<OficioListResponse> {
    let params = new HttpParams()
      .set('page', page.toString())
      .set('per_page', perPage.toString());
    if (anio) params = params.set('anio', anio.toString());
    return this.http.get<OficioListResponse>(this.apiUrl, { params });
  }

  buscar(filtros: any): Observable<BusquedaResponse> {
    let params = new HttpParams();
    Object.keys(filtros).forEach(key => {
      if (filtros[key]) params = params.set(key, filtros[key]);
    });
    return this.http.get<BusquedaResponse>(`${this.apiUrl}/buscar`, { params });
  }

  obtenerSiguienteFolio(anio: number): Observable<{ anio: number; siguiente_folio: number }> {
    return this.http.get<{ anio: number; siguiente_folio: number }>(
      `${this.apiUrl}/siguiente-folio`, { params: { anio: anio.toString() } }
    );
  }

  crear(data: any): Observable<any> {
    return this.http.post(this.apiUrl, data);
  }

  obtener(id: number): Observable<Oficio> {
    return this.http.get<Oficio>(`${this.apiUrl}/${id}`);
  }

  actualizar(id: number, data: any): Observable<any> {
    return this.http.put(`${this.apiUrl}/${id}`, data);
  }

  cancelar(id: number, motivo: string): Observable<any> {
    return this.http.delete(`${this.apiUrl}/${id}`, { body: { motivo } });
  }

  estadisticas(anio?: number): Observable<Estadisticas> {
    let params = new HttpParams();
    if (anio) params = params.set('anio', anio.toString());
    return this.http.get<Estadisticas>(`${this.apiUrl}/estadisticas`, { params });
  }
}
