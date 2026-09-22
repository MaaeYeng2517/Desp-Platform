env "local" {
  url = "postgres://dataeng:dataeng@localhost:15432/datawarehouse?sslmode=disable"
  src = "file://schema.sql"
  dev = "docker://postgres/17/dev"

  migration {
    dir = "file://migrations"
  }

  format {
    migrate {
      diff = "{{ sql . \"  \" }}"
    }
  }
}
