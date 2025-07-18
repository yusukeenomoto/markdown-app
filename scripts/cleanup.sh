running_containers=($(docker ps --format '{{.Names}}'))
if [ "${#running_containers[@]}" -ne 0 ]; then
    for container_name in "${running_containers[@]}"; do   
        docker stop "${container_name}" && docker rm "${container_name}"
    done
else
    echo 'container dose not exist.'
fi