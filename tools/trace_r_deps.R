#!/usr/bin/env Rscript
# R Dependency Tracer
# Parses source() and library() calls from .R files used by run_* scripts.

library(jsonlite)
library(stringr)

# Configure logging
cat("Starting R dependency tracing\n")

# Parse command line arguments
args <- commandArgs(trailingOnly = TRUE)
src_dir <- if(length(args) > 0) args[1] else "R"
scripts_dir <- if(length(args) > 1) args[2] else "."
output_file <- if(length(args) > 2) args[3] else "build/depgraph/depgraph_r.json"
scripts <- if(length(args) > 3) strsplit(args[4], ",")[[1]] else c("run_all.R", "run_modular.R")
verbose <- if(length(args) > 4) as.logical(args[5]) else FALSE

if(verbose) {
  cat("Source directory:", src_dir, "\n")
  cat("Scripts directory:", scripts_dir, "\n")
  cat("Output file:", output_file, "\n")
  cat("Scripts to trace:", paste(scripts, collapse=", "), "\n")
}

# Initialize dependency tracking
dependencies <- list(
  static_imports = character(0),
  dynamic_imports = character(0),
  local_scripts = character(0),
  external_packages = character(0),
  reachable_scripts = character(0)
)

# Function to extract R dependencies from a file
extract_r_dependencies <- function(file_path) {
  if(!file.exists(file_path)) {
    cat("Warning: File", file_path, "not found\n")
    return(list())
  }
  
  content <- readLines(file_path, warn = FALSE)
  deps <- list(
    libraries = character(0),
    sources = character(0),
    requires = character(0)
  )
  
  for(line in content) {
    # Extract library() calls
    library_matches <- str_extract_all(line, "library\\(([^)]+)\\)")
    if(length(library_matches[[1]]) > 0) {
      for(match in library_matches[[1]]) {
        pkg <- str_remove(match, "library\\(")
        pkg <- str_remove(pkg, "\\)")
        pkg <- str_remove_all(pkg, '["\']')
        deps$libraries <- c(deps$libraries, pkg)
      }
    }
    
    # Extract require() calls
    require_matches <- str_extract_all(line, "require\\(([^)]+)\\)")
    if(length(require_matches[[1]]) > 0) {
      for(match in require_matches[[1]]) {
        pkg <- str_remove(match, "require\\(")
        pkg <- str_remove(pkg, "\\)")
        pkg <- str_remove_all(pkg, '["\']')
        deps$requires <- c(deps$requires, pkg)
      }
    }
    
    # Extract source() calls
    source_matches <- str_extract_all(line, "source\\(([^)]+)\\)")
    if(length(source_matches[[1]]) > 0) {
      for(match in source_matches[[1]]) {
        script <- str_remove(match, "source\\(")
        script <- str_remove(script, "\\)")
        script <- str_remove_all(script, '["\']')
        deps$sources <- c(deps$sources, script)
      }
    }
  }
  
  return(deps)
}

# Function to check if a script is local
is_local_script <- function(script_path, base_dir) {
  # Check if it's a relative path or exists in the project
  if(str_detect(script_path, "^\\./") || str_detect(script_path, "^\\.\\.")) {
    return(TRUE)
  }
  
  # Check if it exists in the project directory
  full_path <- file.path(base_dir, script_path)
  if(file.exists(full_path)) {
    return(TRUE)
  }
  
  return(FALSE)
}

# Trace static dependencies from all R files
trace_static_dependencies <- function() {
  cat("Tracing static dependencies\n")
  
  # Find all R files
  r_files <- list.files(scripts_dir, pattern = "\\.R$", recursive = TRUE, full.names = TRUE)
  if(dir.exists(src_dir)) {
    r_files <- c(r_files, list.files(src_dir, pattern = "\\.R$", recursive = TRUE, full.names = TRUE))
  }
  
  cat("Found", length(r_files), "R files\n")
  
  for(r_file in r_files) {
    if(verbose) cat("Processing:", r_file, "\n")
    
    deps <- extract_r_dependencies(r_file)
    
    # Add to dependencies
    dependencies$static_imports <<- c(dependencies$static_imports, deps$libraries, deps$requires)
    
    # Categorize sources
    for(source_script in deps$sources) {
      if(is_local_script(source_script, scripts_dir)) {
        dependencies$local_scripts <<- c(dependencies$local_scripts, source_script)
      }
    }
  }
  
  # Remove duplicates
  dependencies$static_imports <<- unique(dependencies$static_imports)
  dependencies$local_scripts <<- unique(dependencies$local_scripts)
}

# Trace dynamic dependencies from main scripts
trace_dynamic_dependencies <- function(script_files) {
  cat("Tracing dynamic dependencies\n")
  
  for(script_file in script_files) {
    if(!file.exists(script_file)) {
      cat("Warning: Script file", script_file, "not found\n")
      next
    }
    
    cat("Tracing", script_file, "\n")
    
    deps <- extract_r_dependencies(script_file)
    
    # Add to dynamic imports
    dependencies$dynamic_imports <<- c(dependencies$dynamic_imports, deps$libraries, deps$requires)
    dependencies$reachable_scripts <<- c(dependencies$reachable_scripts, deps$sources)
  }
  
  # Remove duplicates
  dependencies$dynamic_imports <<- unique(dependencies$dynamic_imports)
  dependencies$reachable_scripts <<- unique(dependencies$reachable_scripts)
}

# Categorize dependencies
categorize_dependencies <- function() {
  categorized <- list(
    standard_library = character(0),
    third_party = character(0),
    local_project = character(0),
    unknown = character(0)
  )
  
  # Common R standard library packages
  stdlib_packages <- c("base", "utils", "stats", "graphics", "grDevices", "methods", "datasets")
  
  for(pkg in dependencies$static_imports) {
    if(pkg %in% stdlib_packages) {
      categorized$standard_library <- c(categorized$standard_library, pkg)
    } else {
      categorized$third_party <- c(categorized$third_party, pkg)
    }
  }
  
  for(script in dependencies$local_scripts) {
    categorized$local_project <- c(categorized$local_project, script)
  }
  
  return(categorized)
}

# Generate dependency graph
generate_dependency_graph <- function() {
  categorized <- categorize_dependencies()
  
  graph <- list(
    metadata = list(
      src_dir = src_dir,
      scripts_dir = scripts_dir,
      total_files_analyzed = length(list.files(scripts_dir, pattern = "\\.R$", recursive = TRUE))
    ),
    dependencies = list(
      static_imports = sort(unique(dependencies$static_imports)),
      dynamic_imports = sort(unique(dependencies$dynamic_imports)),
      local_scripts = sort(unique(dependencies$local_scripts)),
      external_packages = sort(unique(dependencies$static_imports)),
      reachable_scripts = sort(unique(dependencies$reachable_scripts))
    ),
    categorized = list(
      standard_library = sort(unique(categorized$standard_library)),
      third_party = sort(unique(categorized$third_party)),
      local_project = sort(unique(categorized$local_project)),
      unknown = sort(unique(categorized$unknown))
    )
  )
  
  return(graph)
}

# Main execution
main <- function() {
  # Trace dependencies
  trace_static_dependencies()
  trace_dynamic_dependencies(scripts)
  
  # Generate graph
  graph <- generate_dependency_graph()
  
  # Create output directory
  output_dir <- dirname(output_file)
  if(!dir.exists(output_dir)) {
    dir.create(output_dir, recursive = TRUE)
  }
  
  # Save to file
  tryCatch({
    write_json(graph, output_file, pretty = TRUE, auto_unbox = TRUE)
    cat("Dependency graph saved to", output_file, "\n")
    cat("Found", length(graph$dependencies$static_imports), "static imports\n")
    cat("Found", length(graph$dependencies$dynamic_imports), "dynamic imports\n")
    cat("Found", length(graph$dependencies$local_scripts), "local scripts\n")
    cat("Found", length(graph$dependencies$external_packages), "external packages\n")
    return(0)
  }, error = function(e) {
    cat("Error saving dependency graph:", e$message, "\n")
    return(1)
  })
}

# Run main function
exit_code <- main()
quit(status = exit_code)
