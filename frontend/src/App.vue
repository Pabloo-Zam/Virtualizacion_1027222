<template>
  <div class="page">
    <div class="container">
      <header class="hero">
        <p class="eyebrow"></p>
        <h1>Inscripción de miembros</h1>
        <p class="description">
          
        </p>
      </header>

      <section class="form-card">
        <div class="card-header">
          <h2>{{ modoEdicion ? "Editar inscripción" : "Nueva inscripción" }}</h2>
          <p>
            {{ modoEdicion
              ? "Actualiza los datos del miembro seleccionado."
              : "Completa la información del nuevo miembro." }}
          </p>
        </div>

        <form @submit.prevent="guardarInscripcion" class="form">
          <div class="form-grid">
            <div class="field">
              <label>Nombre completo</label>
              <input
                v-model="form.nombre"
                type="text"
                
              />
            </div>

            <div class="field">
              <label>Correo electrónico</label>
              <input
                v-model="form.correo"
                type="email"
                
              />
            </div>

            <div class="field">
              <label>Teléfono</label>
              <input
                v-model="form.telefono"
                type="text"
                
              />
            </div>

            <div class="field">
              <label>Sede</label>
              <select v-model="form.sede">
                <option value="">Seleccione una sede</option>
                <option value="Sede Central">Sede Central</option>
                <option value="Sede Norte">Sede Norte</option>
                <option value="Sede Sur">Sede Sur</option>
                <option value="Sede Zona 10">Sede Zona 10</option>
              </select>
            </div>

            <div class="field full">
              <label>Plan</label>
              <select v-model="form.plan">
                <option value="">Seleccione un plan</option>
                <option value="Mensual">Mensual</option>
                <option value="Trimestral">Trimestral</option>
                <option value="Anual">Anual</option>
              </select>
            </div>
          </div>

          <div class="actions">
            <button type="submit" class="btn btn-primary">
              {{ modoEdicion ? "Guardar cambios" : "Registrar inscripción" }}
            </button>

            <button
              v-if="modoEdicion"
              type="button"
              class="btn btn-secondary"
              @click="cancelarEdicion"
            >
              Cancelar
            </button>
          </div>
        </form>

        <div v-if="mensaje" :class="['message', tipoMensaje]">
          {{ mensaje }}
        </div>
      </section>

      <section class="records-card">
        <div class="card-header records-header">
          <div>
            <h2>Registros</h2>
            
          </div>

          <button class="btn btn-light" @click="cargarInscripciones">
            Actualizar
          </button>
        </div>

        <div v-if="inscripciones.length === 0" class="empty-state">
          No hay registros todavía.
        </div>

        <div v-else class="records-list">
          <div
            v-for="item in inscripciones"
            :key="item.id"
            class="record-item"
          >
            <div class="record-main">
              <h3>{{ item.nombre }}</h3>
              <p>{{ item.correo }}</p>
              <p>{{ item.telefono }}</p>
            </div>

            <div class="record-extra">
              <span>{{ item.sede }}</span>
              <span>{{ item.plan }}</span>
            </div>

            <div class="record-actions">
              <button class="btn btn-edit" @click="editarInscripcion(item)">
                Editar
              </button>
              <button class="btn btn-delete" @click="eliminarInscripcion(item.id)">
                Eliminar
              </button>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script>
const API_URL = "http://localhost:30081";

export default {
  data() {
    return {
      form: {
        nombre: "",
        correo: "",
        telefono: "",
        sede: "",
        plan: ""
      },
      idEditando: null,
      modoEdicion: false,
      mensaje: "",
      tipoMensaje: "",
      inscripciones: []
    };
  },
  methods: {
    async guardarInscripcion() {
      this.mensaje = "";
      this.tipoMensaje = "";

      if (this.modoEdicion) {
        await this.actualizarInscripcion();
      } else {
        await this.registrarInscripcion();
      }
    },

    async registrarInscripcion() {
      try {
        const response = await fetch(`${API_URL}/api/inscripciones`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify(this.form)
        });

        const data = await response.json();

        if (!response.ok) {
          this.mensaje = data.error || "No se pudo registrar la inscripción";
          this.tipoMensaje = "error";
          return;
        }

        this.mensaje = data.mensaje;
        this.tipoMensaje = "success";
        this.limpiarFormulario();
        this.cargarInscripciones();
      } catch (error) {
        this.mensaje = "Error al conectar con el backend";
        this.tipoMensaje = "error";
      }
    },

    editarInscripcion(item) {
      this.idEditando = item.id;
      this.modoEdicion = true;

      this.form = {
        nombre: item.nombre,
        correo: item.correo,
        telefono: item.telefono,
        sede: item.sede,
        plan: item.plan
      };

      window.scrollTo({
        top: 0,
        behavior: "smooth"
      });
    },

    async actualizarInscripcion() {
      try {
        const response = await fetch(`${API_URL}/api/inscripciones/${this.idEditando}`, {
          method: "PUT",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify(this.form)
        });

        const data = await response.json();

        if (!response.ok) {
          this.mensaje = data.error || "No se pudo actualizar la inscripción";
          this.tipoMensaje = "error";
          return;
        }

        this.mensaje = data.mensaje;
        this.tipoMensaje = "success";
        this.limpiarFormulario();
        this.cargarInscripciones();
      } catch (error) {
        this.mensaje = "Error al conectar con el backend";
        this.tipoMensaje = "error";
      }
    },

    async eliminarInscripcion(id) {
      const confirmar = confirm("¿Deseas eliminar esta inscripción?");

      if (!confirmar) return;

      try {
        const response = await fetch(`${API_URL}/api/inscripciones/${id}`, {
          method: "DELETE"
        });

        const data = await response.json();

        if (!response.ok) {
          this.mensaje = data.error || "No se pudo eliminar la inscripción";
          this.tipoMensaje = "error";
          return;
        }

        this.mensaje = data.mensaje;
        this.tipoMensaje = "success";
        this.cargarInscripciones();
      } catch (error) {
        this.mensaje = "Error al conectar con el backend";
        this.tipoMensaje = "error";
      }
    },

    cancelarEdicion() {
      this.limpiarFormulario();
      this.mensaje = "";
      this.tipoMensaje = "";
    },

    limpiarFormulario() {
      this.form = {
        nombre: "",
        correo: "",
        telefono: "",
        sede: "",
        plan: ""
      };

      this.idEditando = null;
      this.modoEdicion = false;
    },

    async cargarInscripciones() {
      try {
        const response = await fetch(`${API_URL}/api/inscripciones`);
        this.inscripciones = await response.json();
      } catch (error) {
        this.mensaje = "No se pudieron cargar los registros";
        this.tipoMensaje = "error";
      }
    }
  },
  mounted() {
    this.cargarInscripciones();
  }
};
</script>

<style>
* {
  box-sizing: border-box;
}

body {
  margin: 0;
  font-family: Inter, Arial, sans-serif;
  background: #f5f7fb;
  color: #1f2937;
}

.page {
  min-height: 100vh;
  padding: 40px 20px 60px;
}

.container {
  max-width: 920px;
  margin: 0 auto;
}

.hero {
  text-align: center;
  margin-bottom: 32px;
}

.eyebrow {
  display: inline-block;
  margin: 0 0 14px;
  padding: 8px 14px;
  border-radius: 999px;
  background: #e8f0ff;
  color: #2563eb;
  font-weight: 700;
  font-size: 14px;
}

.hero h1 {
  margin: 0;
  font-size: 38px;
  font-weight: 800;
  color: #111827;
}

.description {
  max-width: 600px;
  margin: 12px auto 0;
  font-size: 16px;
  line-height: 1.6;
  color: #6b7280;
}

.form-card,
.records-card {
  background: #ffffff;
  border-radius: 22px;
  padding: 28px;
  box-shadow: 0 14px 40px rgba(15, 23, 42, 0.08);
}

.records-card {
  margin-top: 22px;
}

.card-header {
  margin-bottom: 22px;
}

.card-header h2 {
  margin: 0;
  font-size: 24px;
  color: #111827;
}

.card-header p {
  margin: 8px 0 0;
  color: #6b7280;
}

.form {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 18px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.field.full {
  grid-column: span 2;
}

label {
  font-size: 14px;
  font-weight: 700;
  color: #374151;
}

input,
select {
  width: 100%;
  border: none;
  outline: none;
  padding: 14px 16px;
  border-radius: 14px;
  background: #f3f6fb;
  color: #111827;
  font-size: 15px;
  transition: all 0.2s ease;
}

input:focus,
select:focus {
  background: #eef4ff;
  box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.18);
}

.actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.btn {
  border: none;
  border-radius: 14px;
  padding: 13px 18px;
  font-weight: 700;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn:hover {
  transform: translateY(-1px);
}

.btn-primary {
  background: #2563eb;
  color: white;
}

.btn-primary:hover {
  background: #1d4ed8;
}

.btn-secondary {
  background: #e5e7eb;
  color: #374151;
}

.btn-secondary:hover {
  background: #dbe1e8;
}

.btn-light {
  background: #f3f6fb;
  color: #111827;
}

.btn-light:hover {
  background: #e8eef8;
}

.message {
  margin-top: 18px;
  padding: 14px 16px;
  border-radius: 14px;
  font-weight: 600;
}

.success {
  background: #ecfdf3;
  color: #166534;
}

.error {
  background: #fef2f2;
  color: #991b1b;
}

.records-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.empty-state {
  padding: 22px;
  text-align: center;
  border-radius: 16px;
  background: #f9fafb;
  color: #6b7280;
}

.records-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.record-item {
  display: grid;
  grid-template-columns: 1.5fr 1fr auto;
  gap: 16px;
  align-items: center;
  padding: 18px;
  border-radius: 18px;
  background: #f9fafb;
}

.record-main h3 {
  margin: 0 0 6px;
  font-size: 17px;
  color: #111827;
}

.record-main p {
  margin: 3px 0;
  color: #6b7280;
  font-size: 14px;
}

.record-extra {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.record-extra span {
  display: inline-block;
  width: fit-content;
  padding: 7px 10px;
  border-radius: 999px;
  background: #eef4ff;
  color: #2563eb;
  font-size: 13px;
  font-weight: 700;
}

.record-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.btn-edit {
  background: #f59e0b;
  color: white;
}

.btn-edit:hover {
  background: #d97706;
}

.btn-delete {
  background: #ef4444;
  color: white;
}

.btn-delete:hover {
  background: #dc2626;
}

@media (max-width: 768px) {
  .hero h1 {
    font-size: 30px;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .field.full {
    grid-column: span 1;
  }

  .records-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .record-item {
    grid-template-columns: 1fr;
  }

  .record-actions {
    justify-content: flex-start;
  }
}
</style>