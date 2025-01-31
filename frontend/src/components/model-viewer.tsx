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
	// State Management
	const [isLoading, setIsLoading] = useState<boolean>(true);
	const [object3D, setObject3D] = useState<THREE.Object3D | null>(null);

	// Set obj when it changes
	useEffect(() => {
		if (obj) {
			const loader = new OBJLoader();
			const parsedObject = loader.parse(obj);

			const boundingBox = new THREE.Box3().setFromObject(parsedObject);
			const center = new THREE.Vector3();
			boundingBox.getCenter(center);
			parsedObject.position.sub(center);

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
			<directionalLight position={[-10, 10, -10]} intensity={1} />
			{object3D && <primitive object={object3D} scale={1} />}
			<OrbitControls
				enableZoom={true}
				minDistance={0.5}
				maxDistance={3}
				enableDamping={true}
			/>
		</Canvas>
	);
};

export default ModelViewer;
