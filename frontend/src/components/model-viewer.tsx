import { OrbitControls } from "@react-three/drei";
import { Canvas } from "@react-three/fiber";
import { useEffect, useState } from "react";
import * as THREE from "three";
import { OBJLoader } from "three/addons/loaders/OBJLoader.js";
import LoadingSpinner from "./loading-spinner";

interface ModelProps {
	obj: string | null;
}

const ModelViewer = ({ obj }: ModelProps) => {
	const [isLoading, setIsLoading] = useState<boolean>(true);
	const [object3D, setObject3D] = useState<THREE.Object3D | null>(null);

	useEffect(() => {
		if (obj) {
			const loader = new OBJLoader();
			const parsedObject = loader.parse(obj);
			setObject3D(parsedObject);
			setIsLoading(false);
		}
	}, [obj]);

	if (isLoading) {
		return (
			<div className="flex justify-center items-center w-full h-full">
				<LoadingSpinner />
			</div>
		);
	}

	return (
		<Canvas camera={{ position: [0, 0, 2] }}>
			<ambientLight intensity={0.5} />
			<directionalLight position={[10, 10, 10]} intensity={1} />
			{object3D && <primitive object={object3D} scale={1} />}
			<OrbitControls enableZoom={true} />
		</Canvas>
	);
};

export default ModelViewer;
