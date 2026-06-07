import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({ providedIn: 'root' })
export class ReporteService {
  private apiUrl = `${environment.apiUrl}/reportes`;
  private backupUrl = `${environment.apiUrl}/backup`;

  constructor(private http: HttpClient) {}

  exportarPdf(filtros: any): Observable<Blob> {
    let params = new HttpParams();
    Object.keys(filtros).forEach(key => {
      if (filtros[key]) params = params.set(key, filtros[key]);
    });
    return this.http.get(`${this.apiUrl}/pdf`, {
      params, responseType: 'blob'
    });
  }

  exportarExcel(filtros: any): Observable<Blob> {
    let params = new HttpParams();
    Object.keys(filtros).forEach(key => {
      if (filtros[key]) params = params.set(key, filtros[key]);
    });
    return this.http.get(`${this.apiUrl}/excel`, {
      params, responseType: 'blob'
    });
  }

  crearBackup(): Observable<any> {
    return this.http.post(this.backupUrl, {});
  }

  listarBackups(): Observable<any[]> {
    return this.http.get<any[]>(`${this.backupUrl}/listar`);
  }
}
